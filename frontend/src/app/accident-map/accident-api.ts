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
}

export interface AccidentQuery {
  year: number;
  severity?: string;
  country?: string;
}

@Injectable({ providedIn: 'root' })
export class AccidentApi {
  private readonly http = inject(HttpClient);

  getFilters(): Observable<FilterOptions> {
    return this.http.get<FilterOptions>('/api/accidents/filters');
  }

  list(query: AccidentQuery): Observable<AccidentMapResponse> {
    let params = new HttpParams().set('year', query.year);
    if (query.severity) params = params.set('severity', query.severity);
    if (query.country) params = params.set('country', query.country);
    return this.http.get<AccidentMapResponse>('/api/accidents', { params });
  }

  listForYear(year: number): Observable<AccidentMapResponse> {
    return this.http.get<AccidentMapResponse>(`/api/accidents`, { params: { year } });
  }
}
