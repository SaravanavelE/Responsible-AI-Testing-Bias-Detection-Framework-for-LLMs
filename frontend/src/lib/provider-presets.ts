/** Default model per provider — synced with backend PROVIDER_PRESETS */
export const PROVIDER_DEFAULTS: Record<
  string,
  { api_base_url: string; default_model: string; models: string[] }
> = {
  openai: {
    api_base_url: "https://api.openai.com/v1",
    default_model: "gpt-4o-mini",
    models: ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
  },
  groq: {
    api_base_url: "https://api.groq.com/openai/v1",
    default_model: "grok-3-mini",
    models: ["grok-3-mini", "llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"],
  },
  gemini: {
    api_base_url: "https://generativelanguage.googleapis.com/v1beta",
    default_model: "gemini-1.5-flash",
    models: ["gemini-1.5-pro", "gemini-1.5-flash"],
  },
  claude: {
    api_base_url: "https://api.anthropic.com/v1",
    default_model: "claude-3-5-sonnet-20241022",
    models: ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
  },
  ollama: {
    api_base_url: "http://localhost:11434",
    default_model: "llama3",
    models: ["llama3", "mistral", "codellama"],
  },
  deepseek: {
    api_base_url: "https://api.deepseek.com/v1",
    default_model: "deepseek-chat",
    models: ["deepseek-chat", "deepseek-coder"],
  },
  azure_openai: {
    api_base_url: "https://{resource}.openai.azure.com/openai/deployments/{deployment}",
    default_model: "gpt-4o",
    models: ["gpt-4o"],
  },
  openrouter: {
    api_base_url: "https://openrouter.ai/api/v1",
    default_model: "openai/gpt-4o",
    models: ["openai/gpt-4o", "anthropic/claude-3.5-sonnet"],
  },
  mistral: {
    api_base_url: "https://api.mistral.ai/v1",
    default_model: "mistral-large-latest",
    models: ["mistral-large-latest", "mistral-small-latest"],
  },
  cohere: {
    api_base_url: "https://api.cohere.com/v1",
    default_model: "command-r-plus",
    models: ["command-r-plus", "command-r"],
  },
};

export const PROVIDER_LIST = Object.keys(PROVIDER_DEFAULTS);

export function getProviderPreset(provider: string) {
  return PROVIDER_DEFAULTS[provider.toLowerCase()];
}
