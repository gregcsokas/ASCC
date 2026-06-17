import { Component, signal } from '@angular/core';
import {AccidentMap} from './accident-map/accident-map';

@Component({
  selector: 'app-root',
  imports: [AccidentMap],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('frontend');
}
