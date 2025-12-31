export type CodeOption = { value: string; label: string; active?: boolean };

export const MODEL_PROVIDER_OPTIONS: CodeOption[] = [
  { value: "openai", label: "OpenAI", active: true },
  { value: "anthropic", label: "Anthropic", active: true },
  { value: "google", label: "Google", active: true },
  { value: "mistral", label: "Mistral", active: true },
  { value: "azure_openai", label: "Azure OpenAI", active: true },
  { value: "groq", label: "Groq", active: true },
  { value: "local", label: "Local", active: true },
  { value: "other", label: "Other", active: true },
];

export const MODEL_PURPOSE_OPTIONS: CodeOption[] = [
  { value: "chat", label: "Chat", active: true },
  { value: "embedding", label: "Embedding", active: true },
];
