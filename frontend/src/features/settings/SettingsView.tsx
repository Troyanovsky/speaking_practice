import React, { useState, useEffect } from 'react';
import { settingsApi } from '../../api/client';
import type { UserSettings } from '../../types';

// Languages must match backend TTS service LANGUAGE_CONFIG
const LANGUAGES = ['English', 'Spanish', 'French', 'Italian', 'Portuguese'];
const CEFR_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'];

const SettingsView: React.FC = () => {
    const [settings, setSettings] = useState<UserSettings>({
        primary_language: 'English',
        target_language: 'Spanish',
        proficiency_level: 'A1',
        stop_word: 'stop session',
        tts_speed: 1.0,
        llm_base_url: '',
        llm_api_key: '',
        llm_model: ''
    });
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState<{ text: string, type: 'success' | 'error' } | null>(null);

    useEffect(() => {
        loadSettings();
    }, []);

    const loadSettings = async () => {
        setIsLoading(true);
        try {
            const data = await settingsApi.getSettings();
            setSettings(data);
        } catch (error) {
            console.error("Failed to load settings:", error);
            setMessage({ text: "Failed to load settings.", type: 'error' });
        } finally {
            setIsLoading(false);
        }
    };

    const handleSave = async () => {
        setIsLoading(true);
        setMessage(null);
        try {
            await settingsApi.updateSettings(settings);
            setMessage({ text: "Settings saved successfully!", type: 'success' });

            // Clear successful message after 3 seconds
            setTimeout(() => setMessage(null), 3000);
        } catch (error) {
            console.error("Failed to save settings:", error);
            setMessage({ text: "Failed to save settings.", type: 'error' });
        } finally {
            setIsLoading(false);
        }
    };

    const handleChange = (field: keyof UserSettings, value: string | number) => {
        setSettings(prev => ({ ...prev, [field]: value }));
    };

    return (
        <div className="max-w-2xl mx-auto p-4 bg-white rounded-lg shadow-sm">
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Settings</h2>

            {message && (
                <div className={`mb-4 p-3 rounded ${message.type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                    {message.text}
                </div>
            )}

            <div className="space-y-6">
                {/* Language Preferences */}
                <section>
                    <h3 className="text-lg font-semibold mb-3 text-gray-700">Language Preferences</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Primary Language</label>
                            <select
                                value={settings.primary_language}
                                onChange={(e) => handleChange('primary_language', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                {LANGUAGES.map(lang => (
                                    <option key={lang} value={lang}>{lang}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Target Language</label>
                            <select
                                value={settings.target_language}
                                onChange={(e) => handleChange('target_language', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                {LANGUAGES.map(lang => (
                                    <option key={lang} value={lang}>{lang}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Proficiency Level</label>
                            <select
                                value={settings.proficiency_level}
                                onChange={(e) => handleChange('proficiency_level', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                {CEFR_LEVELS.map(level => (
                                    <option key={level} value={level}>{level}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Stop Word</label>
                            <input
                                type="text"
                                value={settings.stop_word}
                                onChange={(e) => handleChange('stop_word', e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                    </div>
                </section>

                <hr className="border-gray-200" />

                {/* Audio Settings */}
                <section>
                    <h3 className="text-lg font-semibold mb-3 text-gray-700">Audio Settings</h3>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                TTS Speech Speed: {settings.tts_speed?.toFixed(1)}x
                            </label>
                            <input
                                type="range"
                                min="0.5"
                                max="1.5"
                                step="0.1"
                                value={settings.tts_speed || 1.0}
                                onChange={(e) => handleChange('tts_speed', parseFloat(e.target.value))}
                                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                            />
                            <div className="flex justify-between text-xs text-gray-500 mt-1">
                                <span>Slower (0.5x)</span>
                                <span>Normal (1.0x)</span>
                                <span>Faster (1.5x)</span>
                            </div>
                            <p className="text-xs text-gray-500 mt-2">
                                Controls the speed of AI responses during conversation. Lower values are better for beginners.
                            </p>
                        </div>
                    </div>
                </section>

                <hr className="border-gray-200" />

                {/* LLM Configuration */}
                <section>
                    <h3 className="text-lg font-semibold mb-3 text-gray-700">LLM Configuration</h3>
                    <div className="space-y-4">
                        <div className="bg-yellow-50 p-3 rounded-md border border-yellow-200 text-sm text-yellow-800 mb-2">
                            <strong>Security Warning:</strong> API keys are stored in a local, unencrypted JSON file. Use only on a secure, private machine.
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Base URL</label>
                            <input
                                type="text"
                                value={settings.llm_base_url || ''}
                                onChange={(e) => handleChange('llm_base_url', e.target.value)}
                                placeholder="https://api.openai.com/v1"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">API Key</label>
                            <input
                                type="password"
                                value={settings.llm_api_key || ''}
                                onChange={(e) => handleChange('llm_api_key', e.target.value)}
                                placeholder="sk-..."
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Model Name</label>
                            <input
                                type="text"
                                value={settings.llm_model || ''}
                                onChange={(e) => handleChange('llm_model', e.target.value)}
                                placeholder="gpt-4o"
                                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                            />
                        </div>
                    </div>
                </section>

                <div className="pt-4 flex justify-end">
                    <button
                        onClick={handleSave}
                        disabled={isLoading}
                        className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition disabled:opacity-50 font-medium"
                    >
                        {isLoading ? "Saving..." : "Save Settings"}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SettingsView;
