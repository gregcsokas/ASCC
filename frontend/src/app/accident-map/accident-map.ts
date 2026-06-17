import {
  AfterViewInit,
  Component, computed,
  ElementRef, inject, NgZone,
  OnDestroy, signal,
  viewChild,
} from '@angular/core';
import * as L from 'leaflet';
import {AccidentApi, AccidentDetail, FilterOptions} from './accident-api';
import {filters} from 'css-select';

const SEVERITY_COLORS: Record<string, string> = {
  'Fatal': '#ff5252',
  'Non-Fatal': '#ffa726',
  'Incident': '#29b6f6'
};
const UNKNOWN_SEVERITY_COLOR = '#9e9e9e';

function severityColor(severity: string | null): string {
  if (severity && severity in SEVERITY_COLORS) return SEVERITY_COLORS[severity];
  return UNKNOWN_SEVERITY_COLOR;
}

const SEVERITY_LEGEND = [
  { label: 'Fatal', color: SEVERITY_COLORS['Fatal'] },
  { label: 'Non-Fatal', color: SEVERITY_COLORS['Non-Fatal'] },
  { label: 'Incident', color: SEVERITY_COLORS['Incident'] },
  { label: 'Unknown', color: UNKNOWN_SEVERITY_COLOR },
];

@Component({
  selector: 'app-accident-map',
  template: `
    <div #mapEl class="map"></div>

    @if (filters(); as f) {
      <div class="filters">
        <label>
          <span>Year</span>
          <select [value]="selectedYear()" (change)="onYear($event)">
            @for (y of years(); track y) {
              <option [value]="y">{{ y }}</option>
            }
          </select>
        </label>

        <label>
          <span>Severity</span>
          <select [value]="selectedSeverity()" (change)="onSeverity($event)">
            <option value="">All</option>
            @for (s of f.severities; track s) {
              <option [value]="s">{{ s }}</option>
            }
          </select>
        </label>

        <label>
          <span>Country</span>
          <select [value]="selectedCountry()" (change)="onCountry($event)">
            <option value="">All</option>
            @for (c of f.countries; track c) {
              <option [value]="c">{{ c }}</option>
            }
          </select>
        </label>

        <label>
          <span>Purpose</span>
          <select [value]="selectedFlightPurpose()" (change)="onPurpose($event)">
            <option value="">All</option>
            @for (p of f.flight_purposes; track p) {
              <option [value]="p">{{ p }}</option>
            }
          </select>
        </label>

        <label>
          <span>Phase</span>
          <select [value]="selectedFlightPhase()" (change)="onPhase($event)">
            <option value="">All</option>
            @for (p of f.flight_phases; track p) {
              <option [value]="p">{{ p }}</option>
            }
          </select>
        </label>
      </div>
    }

    <div class="legend">
      @for (e of legend; track e.label) {
        <span class="legend-item"><i class="dot" [style.background]="e.color"></i>{{ e.label }}</span>
      }
    </div>

    @if (detailLoading() || detail() || detailError()) {
      <aside class="detail">
        <button class="close" (click)="closeDetail()" aria-label="Close">×</button>

        @if (detailLoading()) {
          <p class="muted">Loading…</p>
        } @else if (detailError()) {
          <p class="muted">Couldn't load this accident.</p>
        } @else if (detail(); as d) {
          <header>
            <h2>{{ d.location ?? d.event_id }}</h2>
            <p class="muted">{{ d.event_date }}{{ d.country ? ' · ' + d.country : '' }}</p>
            @if (d.max_severity) {
              <span class="badge"><i class="dot" [style.background]="severityColor(d.max_severity)"></i>{{ d.max_severity }}</span>
            }
          </header>

          <dl>
            <dt>Investigation</dt><dd>{{ d.investigation_type }}</dd>
            @if (d.report_status) { <dt>Report</dt><dd>{{ d.report_status }}</dd> }
            @if (d.weather_condition) { <dt>Weather</dt><dd>{{ d.weather_condition }}</dd> }
            @if (d.airport_name || d.airport_code) { <dt>Airport</dt><dd>{{ d.airport_name ?? d.airport_code }}</dd> }
            @if (d.latitude != null && d.longitude != null) { <dt>Coordinates</dt><dd>{{ d.latitude }}, {{ d.longitude }}</dd> }
          </dl>

          <h3>Aircraft ({{ d.aircraft.length }})</h3>
          @for (ac of d.aircraft; track ac.accident_number) {
            <div class="aircraft">
              <strong>{{ ac.manufacturer ?? '—' }} {{ ac.model ?? '' }}</strong>
              <dl>
                @if (ac.category) { <dt>Category</dt><dd>{{ ac.category }}</dd> }
                @if (ac.aircraft_damage) { <dt>Damage</dt><dd>{{ ac.aircraft_damage }}</dd> }
                @if (ac.broad_phase_of_flight) { <dt>Phase</dt><dd>{{ ac.broad_phase_of_flight }}</dd> }
                @if (ac.purpose) { <dt>Purpose</dt><dd>{{ ac.purpose }}</dd> }
                <dt>Injuries</dt>
                <dd>{{ ac.fatal_injuries ?? 0 }} fatal · {{ ac.serious_injuries ?? 0 }} serious · {{ ac.minor_injuries ?? 0 }} minor · {{ ac.uninjured ?? 0 }} uninjured</dd>
              </dl>
            </div>
          }
        }
      </aside>
    }
  `,
  styles: `
    .map { position: fixed; inset: 0; }

    .filters {
      position: fixed; top: 12px; right: 12px; z-index: 1000;
      display: flex; gap: 10px; padding: 10px 12px;
      background: rgba(22,22,26,0.88); border: 1px solid rgba(255,255,255,0.1);
      border-radius: 8px; color: #e8e8e8; font: 13px/1.2 system-ui, sans-serif;
    }
    .filters label { display: flex; flex-direction: column; gap: 4px; }
    .filters span { opacity: 0.7; font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; }
    .filters select {
      background: #2a2a30; color: #e8e8e8; border: 1px solid rgba(255,255,255,0.15);
      border-radius: 5px; padding: 5px 8px;
    }

    .legend {
      position: fixed; bottom: 12px; left: 12px; z-index: 900;
      display: flex; flex-direction: column; gap: 4px; padding: 8px 10px;
      background: rgba(22,22,26,0.88); border: 1px solid rgba(255,255,255,0.1);
      border-radius: 8px; color: #e8e8e8; font: 12px/1.2 system-ui, sans-serif;
    }
    .legend-item { display: flex; align-items: center; gap: 6px; }
    .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }

    .detail {
      position: fixed; top: 0; left: 0; bottom: 0; z-index: 1001;
      width: 320px; max-width: 85vw; overflow-y: auto; padding: 16px 18px;
      background: rgba(18,18,22,0.96); border-right: 1px solid rgba(255,255,255,0.1);
      color: #e8e8e8; font: 13px/1.4 system-ui, sans-serif;
    }
    .detail .close {
      position: absolute; top: 10px; right: 10px; width: 28px; height: 28px;
      background: transparent; color: #aaa; border: none; font-size: 22px; cursor: pointer;
    }
    .detail h2 { margin: 0 0 2px; font-size: 16px; }
    .detail h3 { margin: 16px 0 6px; font-size: 13px; opacity: 0.7; text-transform: uppercase; letter-spacing: 0.04em; }
    .detail .muted { opacity: 0.6; }
    .detail .badge { display: inline-flex; align-items: center; gap: 6px; margin-top: 6px; }
    .detail dl { display: grid; grid-template-columns: auto 1fr; gap: 2px 12px; margin: 8px 0; }
    .detail dt { opacity: 0.6; }
    .detail dd { margin: 0; }
    .detail .aircraft { padding: 8px 0; border-top: 1px solid rgba(255,255,255,0.08);
    }
  `,
})

export class AccidentMap implements AfterViewInit, OnDestroy {
  private readonly mapEl = viewChild.required<ElementRef<HTMLDivElement>>('mapEl');
  private readonly api = inject(AccidentApi);
  private readonly zone = inject(NgZone);

  private map?: L.Map;
  private markers?: L.LayerGroup;

  protected readonly severityColor = severityColor;
  protected readonly legend = SEVERITY_LEGEND;

  protected readonly filters = signal<FilterOptions | null>(null);
  protected readonly selectedYear = signal<number | null>(null);
  protected readonly selectedSeverity = signal('');
  protected readonly selectedCountry = signal('');
  protected readonly selectedFlightPurpose = signal('');
  protected readonly selectedFlightPhase = signal('');

  protected readonly detail = signal<AccidentDetail | null>(null);
  protected readonly detailLoading = signal(false);
  protected readonly detailError = signal(false);

  protected readonly years = computed(() => {
    const f = this.filters();
    return f ? [...f.years].sort((a, b) => b - a) : [];
  });

  ngAfterViewInit(): void {
    this.map = L.map(this.mapEl().nativeElement, {
      center: [39.5, -98.35],
      zoom: 4,
      worldCopyJump: true,
      preferCanvas: true,
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      attribution:
        '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · © <a href="https://carto.com/attributions">CARTO</a>',
    }).addTo(this.map);

    this.markers = L.layerGroup().addTo(this.map);

    this.api.getFilters().subscribe((f) => {
      this.filters.set(f);
      this.selectedYear.set(f.years.length ? Math.max(...f.years) : null);
      this.reload();
    });
  }

  protected onYear(e: Event): void {
    this.selectedYear.set(Number((e.target as HTMLInputElement).value));
    this.reload();
  }

  protected onSeverity(e: Event): void {
    this.selectedSeverity.set((e.target as HTMLInputElement).value);
    this.reload();
  }

  protected onCountry(e: Event): void {
    this.selectedCountry.set((e.target as HTMLSelectElement).value);
    this.reload();
  }

  protected onPurpose(e: Event): void {
    this.selectedFlightPurpose.set((e.target as HTMLSelectElement).value);
    this.reload();
  }

  protected onPhase(e: Event): void {
    this.selectedFlightPhase.set((e.target as HTMLSelectElement).value);
    this.reload();
  }

  protected openDetail(eventId: string): void {
    this.detail.set(null);
    this.detailError.set(false);
    this.detailLoading.set(true);
    this.api.getDetail(eventId).subscribe({
      next: (d) => { this.detail.set(d); this.detailLoading.set(false); },
      error: () => { this.detailError.set(true); this.detailLoading.set(false); },
    });
  }

  protected closeDetail(): void {
    this.detail.set(null);
    this.detailError.set(false);
    this.detailLoading.set(false);
  }

  private reload(): void {
    const year = this.selectedYear();
    if (year == null) return;
    this.closeDetail();

    this.api
      .list({
        year,
        severity: this.selectedSeverity() || undefined,
        country: this.selectedCountry() || undefined,
        purpose: this.selectedFlightPurpose() || undefined,
        phase: this.selectedFlightPhase() || undefined,
      })
      .subscribe((res) => {
        this.markers?.clearLayers();
        for (const item of res.items) {
          const color = severityColor(item.severity);
          const marker = L.circleMarker([item.latitude, item.longitude], {
            radius: 4, color, weight: 1, fillColor: color, fillOpacity: 0.7,
          });
          marker.on('click', () => this.zone.run(() => this.openDetail(item.event_id)));
          marker.addTo(this.markers!);
        }
      });
  }

  ngOnDestroy(): void {
    this.map?.remove();
  }
}
