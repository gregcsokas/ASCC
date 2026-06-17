import {
  AfterViewInit,
  Component,
  ElementRef,
  OnDestroy,
  viewChild,
} from '@angular/core';
import * as L from 'leaflet';

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
  private map?: L.Map;

  ngAfterViewInit(): void {
    this.map = L.map(this.mapEl().nativeElement, {
      center: [39.5, -98.35],
      zoom: 4,
      worldCopyJump: true,
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      attribution:
        '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · © <a href="https://carto.com/attributions">CARTO</a>',
    }).addTo(this.map);
  }

  ngOnDestroy(): void {
    this.map?.remove();
  }
}
