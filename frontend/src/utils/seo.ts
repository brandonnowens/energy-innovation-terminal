import { useEffect } from 'react';

/**
 * Client-Side SEO and Dynamic Meta Tag Management Utility
 */

export interface MetaTagsConfig {
  title: string;
  description: string;
  canonicalUrl?: string;
  ogImage?: string;
  ogType?: string;
  jsonLd?: Record<string, any>;
  keywords?: string[];
}

export function updatePageMeta({
  title,
  description,
  canonicalUrl,
  ogImage,
  ogType = 'website',
  jsonLd,
  keywords,
}: MetaTagsConfig) {
  // 1. Update Title
  const fullTitle = title.includes('Energy Innovation Terminal')
    ? title
    : `${title} | Energy Innovation Terminal`;
  document.title = fullTitle;

  // 2. Helper to set or create meta tags
  const setMeta = (name: string, content: string, isProperty = false) => {
    const attr = isProperty ? 'property' : 'name';
    let el = document.querySelector(`meta[${attr}="${name}"]`) as HTMLMetaElement;
    if (!el) {
      el = document.createElement('meta');
      el.setAttribute(attr, name);
      document.head.appendChild(el);
    }
    el.setAttribute('content', content);
  };

  // 3. Standard Meta
  setMeta('description', description);
  if (keywords && keywords.length > 0) {
    setMeta('keywords', keywords.join(', '));
  }

  // 4. Open Graph
  setMeta('og:title', fullTitle, true);
  setMeta('og:description', description, true);
  setMeta('og:type', ogType, true);
  if (canonicalUrl) {
    setMeta('og:url', canonicalUrl, true);
  }
  if (ogImage) {
    setMeta('og:image', ogImage, true);
  }

  // 5. Twitter Card
  setMeta('twitter:card', ogImage ? 'summary_large_image' : 'summary');
  setMeta('twitter:title', fullTitle);
  setMeta('twitter:description', description);
  if (ogImage) {
    setMeta('twitter:image', ogImage);
  }

  // 6. Canonical Link
  if (canonicalUrl) {
    let link = document.querySelector('link[rel="canonical"]') as HTMLLinkElement;
    if (!link) {
      link = document.createElement('link');
      link.setAttribute('rel', 'canonical');
      document.head.appendChild(link);
    }
    link.setAttribute('href', canonicalUrl);
  }

  // 7. Structured JSON-LD Schema
  if (jsonLd) {
    let script = document.getElementById('page-jsonld') as HTMLScriptElement;
    if (!script) {
      script = document.createElement('script');
      script.id = 'page-jsonld';
      script.type = 'application/ld+json';
      document.head.appendChild(script);
    }
    script.textContent = JSON.stringify(jsonLd);
  }
}

export function useSEO(config: MetaTagsConfig, deps: any[] = []) {
  useEffect(() => {
    updatePageMeta(config);
  }, deps);
}
