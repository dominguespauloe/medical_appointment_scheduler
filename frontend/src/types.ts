export type Intent = 'schedule' | 'cancel' | 'unknown';
export type ResponseStatus = 'success' | 'error' | 'info';

export interface Professional {
  id: string;
  name: string;
  speciality: string;
}

export interface Appointment {
  professionalId: string;
  professionalName: string;
  datetime: string;
  patientName: string;
  reason?: string;
}

export interface IntentData {
  intent: Intent;
  professionalId?: string;
  professionalName?: string;
  datetime?: string;
  patientName?: string;
  reason?: string;
}

export interface ChatResponse {
  intent: Intent;
  status: ResponseStatus;
  message: string;
  data: IntentData;
  appointment?: Appointment;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  response?: ChatResponse;
}
