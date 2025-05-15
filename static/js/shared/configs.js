// Model configurations shared across components
const modelConfigs = {
    gemini: [
        { id: 'gemini-2.0-flash', name: 'Gemini 2.0 Flash', default: true },
        { id: 'gemini-2.5-flash-preview-04-17', name: 'Gemini 2.5 Flash' },
        { id: 'gemini-2.5-pro-preview-05-06', name: 'Gemini 2.5 Pro' }
    ],
    openai: [
        { id: 'gpt-4o-2024-08-06', name: 'GPT-4o', default: true },
        { id: 'o4-mini-2025-04-16', name: 'GPT-4o Mini' },
        { id: 'o3-mini-2025-01-31', name: 'GPT-3o Mini' }
    ]
}; 