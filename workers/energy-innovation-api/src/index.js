import { Container } from "@cloudflare/containers";

const PORT = 8000;

const ALLOWED_ORIGINS = new Set([
  "https://terminal.aixenergy.io",
  "https://energy-innovation-terminal.pages.dev",
  "https://aixenergy.io",
  "https://www.aixenergy.io",
  "http://localhost:5173",
  "http://127.0.0.1:5173",
]);

// Names only. Values come from `wrangler secret put` and are copied into the
// container on start. Empty secrets are omitted so application defaults stay.
const SECRET_KEYS = [
  "DATABASE_URL",
  "OPENAI_API_KEY",
  "ANTHROPIC_API_KEY",
  "GEMINI_API_KEY",
  "JWT_SECRET_KEY",
  "GHOST_ADMIN_API_KEY",
  "GHOST_WEBHOOK_SECRET",
  "ADMIN_GMAIL_PASSWORD",
  "TAVUS_API_KEY",
  "SOCRATA_APP_TOKEN",
  "GRANTS_GOV_API_KEY",
  "SAM_GOV_API_KEY",
];

function containerEnv(env) {
  const envVars = {
    ENVIRONMENT: "production",
    ENABLE_BACKGROUND_SCHEDULERS: "false",
    SKIP_STARTUP_WARM: "true",
    DB_POOL_SIZE: "3",
    DB_MAX_OVERFLOW: "2",
    DB_SSL_MODE: "require",
    PORT: String(PORT),
    WEB_CONCURRENCY: "1",
    CORS_ORIGINS: [...ALLOWED_ORIGINS].join(","),
  };
  for (const key of SECRET_KEYS) {
    const value = env[key];
    if (typeof value === "string" && value.length > 0) {
      envVars[key] = value;
    }
  }
  return envVars;
}

async function secretFingerprint(envVars) {
  const material = SECRET_KEYS.map((key) => `${key}=${envVars[key] ?? ""}`).join("\n");
  const digest = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(material),
  );
  return [...new Uint8Array(digest)]
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

function allowedOrigin(request) {
  const origin = request.headers.get("Origin");
  if (origin && ALLOWED_ORIGINS.has(origin)) return origin;
  return "https://terminal.aixenergy.io";
}

function corsHeaders(request) {
  return {
    "access-control-allow-origin": allowedOrigin(request),
    "access-control-allow-credentials": "true",
    "access-control-allow-methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
    "access-control-allow-headers":
      request.headers.get("Access-Control-Request-Headers") || "*",
    "access-control-max-age": "86400",
    vary: "Origin",
  };
}

export class EnergyApiContainer extends Container {
  defaultPort = PORT;
  sleepAfter = "15m";
  enableInternet = true;
  // Readiness is "uvicorn is listening". /health also pings Postgres and can
  // exceed the helper's 5s probe, so this hits `/`, which 404s quickly
  // when the API image has no frontend bundle.
  pingEndpoint = "container/";

  constructor(ctx, env) {
    super(ctx, env);
    this.envVars = containerEnv(env);
  }

  // Secrets are fixed on a running container process. When Worker secrets change,
  // stop that process so the next start receives the new values.
  async recycleContainerIfSecretsChanged() {
    this.envVars = containerEnv(this.env);
    const next = await secretFingerprint(this.envVars);
    const previous = await this.ctx.storage.get("secret-fingerprint");
    const container = this.ctx.container;
    if (container?.running && previous !== next) {
      try {
        await this.destroy();
      } catch {
        await this.stop("SIGKILL");
      }
      for (let attempt = 0; attempt < 40 && container.running; attempt++) {
        await scheduler.wait(250);
      }
      if (container.running) {
        throw new Error("Container did not stop after the Worker secrets changed");
      }
    }
    return next;
  }

  async fetch(request) {
    let fingerprint;
    try {
      fingerprint = await this.recycleContainerIfSecretsChanged();
      await this.startAndWaitForPorts({
        ports: [PORT],
        startOptions: {
          envVars: this.envVars,
          enableInternet: true,
        },
        cancellationOptions: {
          instanceGetTimeoutMS: 45_000,
          portReadyTimeoutMS: 120_000,
        },
      });
      await this.ctx.storage.put("secret-fingerprint", fingerprint);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      return Response.json(
        { status: "error", detail: `API container failed to start: ${message}` },
        { status: 503, headers: corsHeaders(request) },
      );
    }
    return this.containerFetch(request);
  }
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(request) });
    }
    if (!env.DATABASE_URL) {
      return Response.json(
        {
          status: "error",
          detail:
            "DATABASE_URL is not set on the energy-innovation-api Worker. From workers/energy-innovation-api run: npx wrangler secret put DATABASE_URL",
        },
        { status: 500, headers: corsHeaders(request) },
      );
    }
    return env.ENERGY_API.getByName("primary").fetch(request);
  },
};
