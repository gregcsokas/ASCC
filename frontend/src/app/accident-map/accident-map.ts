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
  templateUrl: './accident-map.html',
  styleUrl: './accident-map.css',
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
