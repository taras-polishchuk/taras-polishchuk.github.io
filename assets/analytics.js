window.ANALYTICS_CONFIG = Object.assign({
  clarityProjectId: 'wv916p35jj',
  posthogApiKey: 'phc_ni...FoND',
  posthogApiHost: 'https://eu.i.posthog.com',
  gaTrackingId: 'G-8RQ3J37DYE',
  debug: false
}, window.ANALYTICS_CONFIG || {});


const ANALYTICS_CONFIG = {
  storageKey: 'tp-analytics-attribution-v1',
  engagementDelayMs: 30000,
  scrollMarks: [25, 50, 75, 90],
  ...window.ANALYTICS_CONFIG
};

const analytics = window.analytics = (() => {
  const params = new URLSearchParams(window.location.search);
  const trackingKeys = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'gclid', 'fbclid', 'msclkid'];
  const refValue = params.get('ref') || '';
  const variant = refValue === 'frontend'
    ? 'frontend'
    : refValue === 'shopify'
      ? 'shopify'
      : 'default';
  const pageSessionStartedAt = Date.now();
  let engagedSent = false;

  const compactObject = (input) => Object.fromEntries(
    Object.entries(input).filter(([, value]) => value !== '' && value !== null && value !== undefined)
  );

  function readStoredAttribution() {
    try {
      const stored = window.localStorage.getItem(ANALYTICS_CONFIG.storageKey);
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      return null;
    }
  }

  function writeStoredAttribution(value) {
    try {
      window.localStorage.setItem(ANALYTICS_CONFIG.storageKey, JSON.stringify(value));
    } catch (error) {
      return;
    }
  }

  function isExternalReferrer(referrer) {
    if (!referrer) return false;

    try {
      return new URL(referrer).hostname !== window.location.hostname;
    } catch (error) {
      return false;
    }
  }

  function getIncomingTouchBase() {
    return compactObject({
      utm_source: params.get('utm_source') || '',
      utm_medium: params.get('utm_medium') || '',
      utm_campaign: params.get('utm_campaign') || '',
      utm_content: params.get('utm_content') || '',
      utm_term: params.get('utm_term') || '',
      gclid: params.get('gclid') || '',
      fbclid: params.get('fbclid') || '',
      msclkid: params.get('msclkid') || '',
      referrer: isExternalReferrer(document.referrer) ? document.referrer : '',
      landing_page: window.location.href,
      landing_path: window.location.pathname
    });
  }

  function buildStoredAttribution() {
    const stored = readStoredAttribution() || {};
    const incomingTouchBase = getIncomingTouchBase();
    const hasIncomingSignal = trackingKeys.some((key) => Boolean(incomingTouchBase[key])) || Boolean(incomingTouchBase.referrer);
    const timestamp = new Date().toISOString();

    const nextAttribution = {
      firstTouch: stored.firstTouch || null,
      lastTouch: stored.lastTouch || stored.firstTouch || null,
      sessionContext: {
        ref: refValue,
        variant,
        user_agent: navigator.userAgent,
        locale: navigator.language || ''
      },
      updated_at: timestamp
    };

    if (hasIncomingSignal) {
      if (!nextAttribution.firstTouch) {
        nextAttribution.firstTouch = {
          ...incomingTouchBase,
          first_seen_at: timestamp
        };
      }

      nextAttribution.lastTouch = {
        ...incomingTouchBase,
        last_seen_at: timestamp
      };
    }

    writeStoredAttribution(nextAttribution);
    return nextAttribution;
  }

  const attribution = buildStoredAttribution();

  function flattenTouch(prefix, touch) {
    if (!touch) return {};

    return compactObject({
      [`${prefix}_utm_source`]: touch.utm_source,
      [`${prefix}_utm_medium`]: touch.utm_medium,
      [`${prefix}_utm_campaign`]: touch.utm_campaign,
      [`${prefix}_utm_content`]: touch.utm_content,
      [`${prefix}_utm_term`]: touch.utm_term,
      [`${prefix}_gclid`]: touch.gclid,
      [`${prefix}_fbclid`]: touch.fbclid,
      [`${prefix}_msclkid`]: touch.msclkid,
      [`${prefix}_referrer`]: touch.referrer,
      [`${prefix}_landing_path`]: touch.landing_path,
      [`${prefix}_seen_at`]: touch.first_seen_at || touch.last_seen_at
    });
  }

  function getPosthogSuperProperties() {
    return compactObject({
      variant,
      ref: refValue,
      ...flattenTouch('first', attribution.firstTouch),
      ...flattenTouch('last', attribution.lastTouch)
    });
  }

  function initClarity() {
    if (!ANALYTICS_CONFIG.clarityProjectId) return;

    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r);
      t.async = 1;
      t.src = 'https://www.clarity.ms/tag/' + i;
      y = l.getElementsByTagName(r)[0];
      y.parentNode.insertBefore(t, y);
    })(window, document, 'clarity', 'script', ANALYTICS_CONFIG.clarityProjectId);

    const clarityTags = compactObject({
      variant,
      ref: refValue,
      utm_source: attribution.lastTouch && attribution.lastTouch.utm_source,
      utm_medium: attribution.lastTouch && attribution.lastTouch.utm_medium,
      utm_campaign: attribution.lastTouch && attribution.lastTouch.utm_campaign
    });

    Object.entries(clarityTags).forEach(([key, value]) => {
      window.clarity('set', key, String(value));
    });
  }

  function initPostHog() {
    if (!ANALYTICS_CONFIG.posthogApiKey) return;

    !function (t, e) {
      let o;
      let n;
      let p;
      let r;
      if (e.__SV) return;
      window.posthog = e;
      e._i = [];
      e.init = function (apiKey, config, name) {
        function g(target, methodName) {
          const split = methodName.split('.');
          if (split.length === 2) {
            target = target[split[0]];
            methodName = split[1];
          }
          target[methodName] = function () {
            target.push([methodName].concat(Array.prototype.slice.call(arguments, 0)));
          };
        }

        p = t.createElement('script');
        p.type = 'text/javascript';
        p.async = true;
        p.crossOrigin = 'anonymous';
        p.src = config.api_host.replace('.i.posthog.com', '-assets.i.posthog.com') + '/static/array.js';
        r = t.getElementsByTagName('script')[0];
        r.parentNode.insertBefore(p, r);

        let instance = e;
        if (name !== undefined) {
          instance = e[name] = [];
        } else {
          name = 'posthog';
        }

        instance.people = instance.people || [];
        instance.toString = function (stub) {
          let string = 'posthog';
          if (name !== 'posthog') string += '.' + name;
          if (!stub) string += ' (stub)';
          return string;
        };
        instance.people.toString = function () {
          return instance.toString(1) + '.people (stub)';
        };

        const methods = 'capture identify alias people.set people.set_once register register_once unregister reset opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing startSessionRecording stopSessionRecording sessionRecordingStarted get_distinct_id set_config getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags onFeatureFlags onSessionId'.split(' ');
        for (o = 0; o < methods.length; o += 1) g(instance, methods[o]);
        e._i.push([apiKey, config, name]);
      };
      e.__SV = 1;
    }(document, window.posthog || []);

    window.posthog.init(ANALYTICS_CONFIG.posthogApiKey, {
      api_host: ANALYTICS_CONFIG.posthogApiHost,
      autocapture: false,
      capture_pageview: false,
      capture_pageleave: true,
      disable_session_recording: true,
      cross_subdomain_cookie: false
    });

    const superProperties = getPosthogSuperProperties();
    const firstTouchProps = compactObject({
      first_utm_source: superProperties.first_utm_source,
      first_utm_medium: superProperties.first_utm_medium,
      first_utm_campaign: superProperties.first_utm_campaign,
      first_utm_content: superProperties.first_utm_content,
      first_utm_term: superProperties.first_utm_term,
      first_gclid: superProperties.first_gclid,
      first_fbclid: superProperties.first_fbclid,
      first_msclkid: superProperties.first_msclkid,
      first_referrer: superProperties.first_referrer,
      first_landing_path: superProperties.first_landing_path,
      first_seen_at: superProperties.first_seen_at
    });

    const lastTouchProps = compactObject({
      variant: superProperties.variant,
      ref: superProperties.ref,
      last_utm_source: superProperties.last_utm_source,
      last_utm_medium: superProperties.last_utm_medium,
      last_utm_campaign: superProperties.last_utm_campaign,
      last_utm_content: superProperties.last_utm_content,
      last_utm_term: superProperties.last_utm_term,
      last_gclid: superProperties.last_gclid,
      last_fbclid: superProperties.last_fbclid,
      last_msclkid: superProperties.last_msclkid,
      last_referrer: superProperties.last_referrer,
      last_landing_path: superProperties.last_landing_path,
      last_seen_at: superProperties.last_seen_at
    });

    if (Object.keys(firstTouchProps).length) {
      window.posthog.register_once(firstTouchProps);
    }

    if (Object.keys(lastTouchProps).length) {
      window.posthog.register(lastTouchProps);
    }
  }

  function track(eventName, props = {}) {
    const payload = compactObject({
      page_path: window.location.pathname,
      page_url: window.location.href,
      page_title: document.title,
      variant,
      ref: refValue,
      ...props
    });

    if (ANALYTICS_CONFIG.debug) {
      console.info('[analytics]', eventName, payload);
    }

    if (window.posthog && typeof window.posthog.capture === 'function') {
      window.posthog.capture(eventName, payload);
    }

    if (window.gtag && ANALYTICS_CONFIG.gaTrackingId) {
      const gaPayload = ANALYTICS_CONFIG.debug ? { ...payload, debug_mode: false } : payload;
      window.gtag('event', eventName, gaPayload);
    }
  }

  function maybeTrackEngagedVisit() {
    if (engagedSent) return;
    if (Date.now() - pageSessionStartedAt < ANALYTICS_CONFIG.engagementDelayMs) return;
    if (document.visibilityState !== 'visible') return;

    engagedSent = true;
    track('engaged_30s', { seconds_engaged: 30 });
    document.removeEventListener('visibilitychange', maybeTrackEngagedVisit);
  }

  initClarity();
  initPostHog();

  window.setTimeout(maybeTrackEngagedVisit, ANALYTICS_CONFIG.engagementDelayMs);
  document.addEventListener('visibilitychange', maybeTrackEngagedVisit);

  track('page_view');
  track('hero_variant_viewed');

  return {
    track,
    getVariant() {
      return variant;
    },
    getRef() {
      return refValue;
    },
    getAttribution() {
      return attribution;
    }
  };
})();
