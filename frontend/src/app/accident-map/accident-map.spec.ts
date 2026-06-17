import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AccidentMap } from './accident-map';

describe('AccidentMap', () => {
  let component: AccidentMap;
  let fixture: ComponentFixture<AccidentMap>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AccidentMap],
    }).compileComponents();

    fixture = TestBed.createComponent(AccidentMap);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
