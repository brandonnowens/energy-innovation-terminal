"""Models package - imports all declarative SQLAlchemy models."""

from app.models.organization import Organization, OrganizationAlias
from app.models.contact import Contact
from app.models.opportunity import (
    Opportunity, OpportunityCategory, EligibilityRule, OpportunityRestriction
)
from app.models.opportunity_organization import OpportunityOrganization
from app.models.program import Program, ProgramFocusArea
from app.models.award import Award, AwardResult
from app.models.recipient import Recipient
from app.models.project import HistoricalOpportunity, HistoricalProject
from app.models.source import Source, SourceConflict, IngestionRun
from app.models.analysis import ProjectAnalysis
from app.models.relationship import OpportunityRelationship
from app.models.community import CreatorToken, Strategy, Report, SavedChart
from app.models.result import (
    OpportunityResult, SuccessStory, ResultBenchmark, ResultArtifact
)
from app.models.proposal import Proposal
from app.models.user import User, PasswordResetToken
from app.models.attribution import RecipientPatent, RecipientInvestment
from app.models.technology import (
    TechnologyCategory,
    Technology,
    TechnologyCostPerformance,
    TechnologyKPI,
    TechnologySubsystem
)
from app.models.policy import (
    PolicyStandard,
    PolicyTechnologyLink,
    PolicyFuelLink,
    PolicyOpportunityLink,
    PolicyOrganizationLink,
    RegulatoryProceeding,
    ProceedingTechnologyLink,
    ProceedingOrganizationLink,
    ProceedingOpportunityLink
)
from app.models.admin_email import (
    AdminEmailCampaign,
    AdminEmailLog,
    ContactEmailThread,
    ContactEmailMessage
)
from app.models.news import NewsItem, NewsItemLink
from app.models.foa_shred import FoaShredResult
from app.models.alert import AlertSubscription, AlertTriggerLog
from app.models.interconnection import InterconnectionQueueProject
from app.models.lab_facility import NationalLabFacility, FacilityTechnologyLink
from app.models.sec_form_d import SecFormDFiling
from app.models.scaleup_capital import FederalScaleupAllocation
from app.models.procurement import FederalProcurementContract
from app.models.der_market import DerMarketDeployment
from app.models.university_ip import UniversityLicensableTechnology

