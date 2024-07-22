import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Location } from '@angular/common';
import { FileUploadComponent } from "./shared/file-upload/file-upload.component";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, FileUploadComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  constructor(private _location: Location) 
  {}

  backClicked() {
    this._location.back();
  }
 }
