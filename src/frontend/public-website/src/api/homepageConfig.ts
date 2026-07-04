import { apiCall } from './client';

export interface Sponsor {
  name: string;
  logo_url: string;
  website_url: string;
}

export interface HomepageConfig {
  title: string;
  subtitle: string;
  welcome_message: string;
  about_us: string;
  hero_image_url: string | null;
  sponsors: Sponsor[];
}

export const homepageConfigApi = {
  async getHomepageConfig(): Promise<HomepageConfig> {
    return apiCall<HomepageConfig>('/home-page-config');
  },
};
