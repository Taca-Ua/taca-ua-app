import { apiClient } from './client';

// Participant interface (students)
export interface Participant {
  id: number;
  course_id: string;
  full_name: string;
  is_member: boolean;
  student_number: string;
}

export interface ParticipantCreate {
  full_name: string;
  course_id: string;
  student_number: string;
  is_member: boolean;
}

export interface ParticipantUpdate {
  full_name?: string;
  course_id?: string;
  student_number?: string;
  is_member?: boolean;
}

// Staff interface
export interface Staff {
  id: number;
  full_name: string;
  contact?: string;
  staff_number?: string;
}

export interface StaffCreate {
  full_name: string;
  contact?: string;
  staff_number?: string;
}

export interface StaffUpdate {
  full_name?: string;
  contact?: string;
  staff_number?: string;
}

// Unified member type for display
export type UnifiedMember =
  | (Participant & { memberType: 'participant' })
  | (Staff & { memberType: 'staff' });

// Participants API
export const participantsApi = {
  async getAll(): Promise<Participant[]> {
    return apiClient.get<Participant[]>('/students');
  },

  async getById(id: number): Promise<Participant> {
    return apiClient.get<Participant>(`/students/${id}`);
  },

  async create(data: ParticipantCreate): Promise<Participant> {
    return apiClient.post<Participant>('/students', data);
  },

  async update(id: number, data: ParticipantUpdate): Promise<Participant> {
    return apiClient.put<Participant>(`/students/${id}`, data);
  },

  async delete(id: number): Promise<void> {
    return apiClient.delete(`/students/${id}`);
  },
};

// Staff API
export const staffApi = {
  async getAll(): Promise<Staff[]> {
    return apiClient.get<Staff[]>('/staff');
  },

  async getById(id: number): Promise<Staff> {
    return apiClient.get<Staff>(`/staff/${id}`);
  },

  async create(data: StaffCreate): Promise<Staff> {
    return apiClient.post<Staff>('/staff', data);
  },

  async update(id: number, data: StaffUpdate): Promise<Staff> {
    return apiClient.put<Staff>(`/staff/${id}`, data);
  },

  async delete(id: number): Promise<void> {
    return apiClient.delete(`/staff/${id}`);
  },
};
