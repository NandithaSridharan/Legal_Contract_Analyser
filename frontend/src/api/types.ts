export interface Contract { id: number; filename: string; title?: string; text?: string; summary?: string; created_at?: string; updated_at?: string; analysis_status?: string; risk_score?: number; risk_level?: string; pending_obligations?: number; }
export interface Clause { id?: number; category: string; text: string; risk_level?: string; }
export interface Risk { id?: number; category: string; clause: string; risk_score: number; risk_level: string; reason: string; }
export interface Entity { id?: number; entity_type: string; entity_value: string; type?: string; value?: string; }
export interface Obligation { id: number; obligation: string; responsible_party?: string; deadline?: string; frequency?: string; category?: string; completed: boolean; }
export interface UploadResponse { success: boolean; contract_id: string; filename: string; num_chunks: number; database_id?: number; }
export interface ChatResponse { answer: string; sources: string[]; }
export interface FullContract { success: boolean; contract: Contract; clauses: Clause[]; risks: Risk[]; entities: Entity[]; obligations: Obligation[]; }
export interface AnalysisResponse { success: boolean; contract_id: string; database_id: number; summary?: string; clauses?: Clause[]; risk_analysis?: { risks?: Risk[]; overall_risk_score?: number; overall_risk_level?: string; summary?: { high_risk?: number; medium_risk?: number; low_risk?: number } }; entities?: Record<string, unknown> | Entity[]; obligations?: Obligation[]; checklist?: unknown; }
