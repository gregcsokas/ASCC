import {
  AfterViewInit,
  Component,
  ElementRef, inject,
  OnDestroy,
  viewChild,
} from '@angular/core';
import * as L from 'leaflet';
import {AccidentApi} from './accident-api';

@Component({
  selector: 'app-accident-map',
  template: `<div #mapEl class="map"></div>`,
  styles: `
    .map {
      position: fixed;
      inset: 0;
    }
  `,
})
export class AccidentMap implements AfterViewInit, OnDestroy {
  private readonly mapEl = viewChild.required<ElementRef<HTMLDivElement>>('mapEl');
  private readonly api = inject(AccidentApi);
  private map?: L.Map;
  private markers?: L.LayerGroup;

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

    this.loadYear(2019);
  }

  private loadYear(year: number): void {
    this.api.listForYear(year).subscribe((response) => {
      this.markers?.clearLayers();
      for (const item of response.items) {
        L.circleMarker([item.latitude, item.longitude], {
          radius: 4,
          color: '#ff5252',
          weight: 1,
          fillColor: '#ff5252',
          fillOpacity: 0.7,
        })
          .bindPopup(
            `<strong>${item.location ?? 'Unknown'}</strong><br><small>${item.event_date}</small>`
          )
          .addTo(this.markers!);
      }
      console.log(`${year}: ${response.mapped_count} / ${response.total_count} has coordinates`);
      }
    )
  }

  ngOnDestroy(): void {
    this.map?.remove();
  }
}
