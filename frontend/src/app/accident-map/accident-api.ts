import {inject, Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {Observable} from 'rxjs';


export interface AccidentMapItem {
  id: number;
  event_id: string;
  event_date: string;
  latitude: number;
  longitude: number;
  location: string | null;
  severity: string | null;
  investigation_type: string;
}

export interface AccidentMapResponse {
  year: number;
  total_count: number;
  mapped_count: number;
  items: AccidentMapItem[];
}

export interface FilterOptions {
  years: number[];
  severities: string[];
  countries: string[];
  aircraft_categories: string[];
  flight_purposes: string[];
  flight_phases: string[];
}

export interface AccidentQuery {
  year: number;
  severity?: string;
  country?: string;
  purpose?: string;
  phase?: string;
}

export interface AircraftDetail {
  accident_number: string;
  manufacturer: string | null;
  model: string | null;
  category: string | null;
  engine_type: string | null;
  number_of_engines: number | null;
  aircraft_damage: string | null;
  severity: string | null;
  fatal_injuries: number | null;
  serious_injuries: number | null;
  minor_injuries: number | null;
  uninjured: number | null;
  broad_phase_of_flight: string | null;
  purpose: string | null;
}

export interface AccidentDetail {
  id: number;
  event_id: string;
  event_date: string;
  location: string | null;
  country: string | null;
  latitude: number | null;
  longitude: number | null;
  airport_code: string | null;
  airport_name: string | null;
  weather_condition: string | null;
  investigation_type: string;
  report_status: string | null;
  max_severity: string | null;
  aircraft: AircraftDetail[];
}

@Injectable({ providedIn: 'root' })
export class AccidentApi {
  private readonly http = inject(HttpClient);

  getFilters(): Observable<FilterOptions> {
    return this.http.get<FilterOptions>('/api/accidents/filters');
  }

  getDetail(eventId: string): Observable<AccidentDetail> {
    return this.http.get<AccidentDetail>(`/api/accidents/${encodeURIComponent(eventId)}`);
  }

  list(query: AccidentQuery): Observable<AccidentMapResponse> {
    let params = new HttpParams().set('year', query.year);
    if (query.severity) params = params.set('severity', query.severity);
    if (query.country) params = params.set('country', query.country);
    if (query.purpose) params = params.set('purpose', query.purpose);
    if (query.phase) params = params.set('phase', query.phase);
    return this.http.get<AccidentMapResponse>('/api/accidents', { params });
  }
}
