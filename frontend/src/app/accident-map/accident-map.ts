import {
  AfterViewInit,
  Component, computed,
  ElementRef, inject,
  OnDestroy, signal,
  viewChild,
} from '@angular/core';
import * as L from 'leaflet';
import {AccidentApi, FilterOptions} from './accident-api';
import {filters} from 'css-select';

const SEVERRITY_COLORS: Record<string, string> = {
  'Fatal': '#ff5252',
  'Non-Fatal': '#ffa726',
  'Incident': '#29b6f6'
};
const UNKNOWN_SEVERITY_COLOR = '#9e9e9e';

function severityColor(severity: string | null): string {
  if (severity && severity in SEVERRITY_COLORS) return SEVERRITY_COLORS[severity];
  return UNKNOWN_SEVERITY_COLOR;
}

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
      </div>
    }
  `,
  styles: `
    .map {
      position: fixed;
      inset: 0;
    }

    .filters {
      position: fixed;
      top: 12px;
      right: 12px;
      z-index: 1000;
      display: flex;
      gap: 10px;
      padding: 10px 12px;
      background: rgba(22, 22, 26, 0.88);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 8px;
      color: #e8e8e8;
      font: 13px/1.2 system-ui, sans-serif;
    }
    .filters label { display: flex; flex-direction: column; gap: 4px; }
    .filters span { opacity: 0.7; font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; }
    .filters select {
      background: #2a2a30;
      color: #e8e8e8;
      border: 1px solid rgba(255, 255, 255, 0.15);
      border-radius: 5px;
      padding: 5px 8px;
    }
  `,
})

export class AccidentMap implements AfterViewInit, OnDestroy {
  private readonly mapEl = viewChild.required<ElementRef<HTMLDivElement>>('mapEl');
  private readonly api = inject(AccidentApi);

  private map?: L.Map;
  private markers?: L.LayerGroup;

  protected readonly filters = signal<FilterOptions | null>(null);
  protected readonly selectedYear = signal<number | null>(null);
  protected readonly selectedSeverity = signal('');
  protected readonly selectedCountry = signal('');

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

  private reload(): void {
    const year = this.selectedYear();
    if (year == null) return;

    this.api
      .list({
        year,
        severity: this.selectedSeverity() || undefined,
        country: this.selectedCountry() || undefined,
      })
      .subscribe((res) => {
        this.markers?.clearLayers();
        for (const item of res.items) {
          const color = severityColor(item.severity);
          L.circleMarker([item.latitude, item.longitude], {
            radius: 4,
            color,
            weight: 1,
            fillColor: color,
            fillOpacity: 0.7,
          })
            .bindPopup(
              `<strong>${item.location ?? 'Unknown'}</strong><br>${item.event_date}` +
                (item.severity ? `<br>${item.severity}` : ''),
            )
            .addTo(this.markers!);
        }
      });
  }

  ngOnDestroy(): void {
    this.map?.remove();
  }
}
