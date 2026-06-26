import { apiClient } from "./client";

export interface PlataformHomepageConfig {
    title: string;
    subtitle: string;
    welcome_message: string;
    about_us: string;
    hero_image_url: string;
}

export interface PlataformHomepageConfigUpdate {
    title?: string;
    subtitle?: string;
    welcome_message?: string;
    about_us?: string;
    hero_image?: File;
}

export const plataformConfigsApi = {
    async getPublicHomepageConfig(): Promise<PlataformHomepageConfig> {
        return apiClient.get<PlataformHomepageConfig>('/plataform-configs/public-homepage-config/');
    },

    async updatePublicHomepageConfig(config: PlataformHomepageConfigUpdate): Promise<PlataformHomepageConfig> {
        const formData = new FormData();
        if (config.title !== undefined) formData.append('title', config.title);
        if (config.subtitle !== undefined) formData.append('subtitle', config.subtitle);
        if (config.welcome_message !== undefined) formData.append('welcome_message', config.welcome_message);
        if (config.about_us !== undefined) formData.append('about_us', config.about_us);
        if (config.hero_image !== undefined) formData.append('hero_image', config.hero_image);

        return apiClient.put<PlataformHomepageConfig>('/plataform-configs/public-homepage-config/', formData);
    }
}
