"""Opportunity relationship detection engine."""
import json
import re
from typing import Dict
from sqlalchemy.orm import Session
from app.models.opportunity import Opportunity, OpportunityCategory
from app.models.relationship import OpportunityRelationship

def detect_relationships(db: Session) -> dict:
    """Scan all opportunities and detect relationships. Run as batch."""
    
    # First, clear existing inferred relationships to start fresh
    db.query(OpportunityRelationship).filter(OpportunityRelationship.is_inferred == True).delete()
    db.commit()
    
    results = {"recurring": 0, "complementary": 0, "stackable": 0, "predecessor": 0}
    
    _detect_recurring(db, results)
    _detect_complementary(db, results)
    _detect_stackable(db, results)
    _detect_predecessor_successor(db, results)
    
    return results

def get_word_set(text: str) -> set:
    if not text:
        return set()
    words = re.findall(r'\b\w+\b', text.lower())
    # remove numbers and common stopwords
    stopwords = {"and", "the", "for", "to", "of", "in", "a", "an", "on", "with", "is", "by"}
    return {w for w in words if w not in stopwords and not w.isdigit()}

def _detect_recurring(db: Session, results: Dict[str, int]) -> None:
    # Same agency, similar solicitation number pattern
    # e.g. PON 4XXX -> PON 5XXX, or GFO-24-XXX -> GFO-25-XXX
    opps = db.query(Opportunity).all()
    agency_opps = {}
    for o in opps:
        if o.agency:
            agency_opps.setdefault(o.agency, []).append(o)
    
    for agency, ops in agency_opps.items():
        for i, op1 in enumerate(ops):
            for op2 in ops[i+1:]:
                # Extract numeric suffix from solicitation number
                match1 = re.search(r'(\d+)', op1.solicitation_number)
                match2 = re.search(r'(\d+)', op2.solicitation_number)
                
                if match1 and match2:
                    words1 = get_word_set(op1.name)
                    words2 = get_word_set(op2.name)
                    
                    if not words1 or not words2:
                        continue
                        
                    overlap = len(words1.intersection(words2))
                    total = max(len(words1), len(words2))
                    
                    if total > 0 and overlap / total > 0.7:
                        rel = OpportunityRelationship(
                            source_opp_id=op1.id,
                            target_opp_id=op2.id,
                            relationship_type="recurring",
                            confidence=0.8,
                            is_inferred=True,
                            rationale=f"Similar solicitation number pattern and high title overlap.",
                            evidence=json.dumps({"overlap_ratio": overlap/total})
                        )
                        db.add(rel)
                        results["recurring"] += 1

    db.commit()

def _detect_complementary(db: Session, results: Dict[str, int]) -> None:
    # Different agencies, overlapping technology categories
    cats = db.query(OpportunityCategory).filter(OpportunityCategory.category_type == 'technology').all()
    opp_cats = {}
    for c in cats:
        opp_cats.setdefault(c.opportunity_id, set()).add(c.category_value.lower())
        
    opps = db.query(Opportunity).all()
    opp_dict = {o.id: o for o in opps}
    
    opp_ids = list(opp_cats.keys())
    for i, id1 in enumerate(opp_ids):
        for id2 in opp_ids[i+1:]:
            o1 = opp_dict.get(id1)
            o2 = opp_dict.get(id2)
            if not o1 or not o2:
                continue
                
            if o1.agency != o2.agency:
                c1 = opp_cats[id1]
                c2 = opp_cats[id2]
                overlap = len(c1.intersection(c2))
                if overlap >= 2:
                    total = max(len(c1), len(c2))
                    confidence = overlap / total if total > 0 else 0
                    rel = OpportunityRelationship(
                        source_opp_id=o1.id,
                        target_opp_id=o2.id,
                        relationship_type="complementary",
                        confidence=confidence,
                        is_inferred=True,
                        rationale=f"Shared {overlap} technology categories across different agencies.",
                        evidence=json.dumps({"shared_categories": list(c1.intersection(c2))})
                    )
                    db.add(rel)
                    results["complementary"] += 1
    db.commit()

def _detect_stackable(db: Session, results: Dict[str, int]) -> None:
    # Find pairs where one covers lower TRL and another higher TRL
    # Simplification for demo purposes: Check same technology categories, different max awards/agencies
    cats = db.query(OpportunityCategory).filter(OpportunityCategory.category_type == 'technology').all()
    opp_cats = {}
    for c in cats:
        opp_cats.setdefault(c.opportunity_id, set()).add(c.category_value.lower())
        
    opps = db.query(Opportunity).all()
    opp_dict = {o.id: o for o in opps}
    
    opp_ids = list(opp_cats.keys())
    for i, id1 in enumerate(opp_ids):
        for id2 in opp_ids[i+1:]:
            o1 = opp_dict.get(id1)
            o2 = opp_dict.get(id2)
            if not o1 or not o2:
                continue
                
            c1 = opp_cats[id1]
            c2 = opp_cats[id2]
            overlap = len(c1.intersection(c2))
            
            # Simple heuristic for stackable: overlapping categories, one has much higher funding
            if overlap >= 1:
                if (o1.max_per_award and o2.max_per_award and 
                    (o1.max_per_award > o2.max_per_award * 5 or o2.max_per_award > o1.max_per_award * 5)):
                    rel = OpportunityRelationship(
                        source_opp_id=o1.id,
                        target_opp_id=o2.id,
                        relationship_type="stackable",
                        confidence=0.7,
                        is_inferred=True,
                        rationale="Overlapping technology areas with complementary funding scales (potential progression).",
                        evidence=json.dumps({"shared_categories": list(c1.intersection(c2))})
                    )
                    db.add(rel)
                    results["stackable"] += 1
    db.commit()

def _detect_predecessor_successor(db: Session, results: Dict[str, int]) -> None:
    # Same agency, similar title (>60% word overlap)
    opps = db.query(Opportunity).all()
    agency_opps = {}
    for o in opps:
        if o.agency:
            agency_opps.setdefault(o.agency, []).append(o)
            
    for agency, ops in agency_opps.items():
        for i, op1 in enumerate(ops):
            for op2 in ops[i+1:]:
                words1 = get_word_set(op1.name)
                words2 = get_word_set(op2.name)
                
                if not words1 or not words2:
                    continue
                    
                overlap = len(words1.intersection(words2))
                total = max(len(words1), len(words2))
                
                if total > 0 and overlap / total > 0.6:
                    rel = OpportunityRelationship(
                        source_opp_id=op1.id,
                        target_opp_id=op2.id,
                        relationship_type="predecessor",
                        confidence=overlap/total,
                        is_inferred=True,
                        rationale="Similar titles within the same agency (likely predecessor/successor).",
                        evidence=json.dumps({"overlap_ratio": overlap/total})
                    )
                    db.add(rel)
                    results["predecessor"] += 1
    db.commit()
