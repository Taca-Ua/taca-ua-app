import { apiClient } from "./client";

export interface Sponsor {
    id: number;
    name: string;
    logo_url: string;
    website_url: string;
}

export interface PlataformHomepageConfig {
    title: string;
    subtitle: string;
    welcome_message: string;
    about_us: string;
    hero_image_url: string;
    sponsors: Sponsor[];
}

export interface PlataformHomepageConfigUpdate {
    title?: string;
    subtitle?: string;
    welcome_message?: string;
    about_us?: string;
    hero_image?: File;
}

export interface SponsorCreate {
    name: string;
    logo: File;
    website_url: string;
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
    },

    async addSponsor(sponsor: SponsorCreate): Promise<Sponsor> {
        const formData = new FormData();
        formData.append('name', sponsor.name);
        formData.append('logo', sponsor.logo);
        formData.append('website_url', sponsor.website_url);

        return apiClient.post<Sponsor>('/plataform-configs/public-homepage-config/sponsors/', formData);
    },

    async removeSponsor(sponsorId: number): Promise<void> {
        await apiClient.delete(`/plataform-configs/public-homepage-config/sponsors/${sponsorId}/`);
    },
}
