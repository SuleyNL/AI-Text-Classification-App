import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SnippetsListComponent } from './snippets-list.component';

describe('SnippetsListComponent', () => {
  let component: SnippetsListComponent;
  let fixture: ComponentFixture<SnippetsListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SnippetsListComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(SnippetsListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
