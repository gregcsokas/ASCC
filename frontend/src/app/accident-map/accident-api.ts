import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
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

@Injectable({ providedIn: 'root' })
export class AccidentApi {
  private readonly http = inject(HttpClient);

  listForYear(year: number): Observable<AccidentMapResponse> {
    return this.http.get<AccidentMapResponse>(`/api/accidents`, { params: { year } });
  }
}
