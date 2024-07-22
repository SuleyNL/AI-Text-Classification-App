import { HttpClient } from '@angular/common/http';
import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentService } from '../../documents/document.service';

import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { FormGroup, FormControl, Validators } from '@angular/forms';

@Component({
  selector: 'app-file-upload',
  standalone: true,
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  templateUrl: './file-upload.component.html',
  styleUrl: './file-upload.component.scss'
})
export class FileUploadComponent {

  myForm = new FormGroup({
    name: new FormControl('', [Validators.required, Validators.minLength(3)]),
    file: new FormControl('', [Validators.required]),
    fileSource: new FormControl('', [Validators.required])
  });

  constructor(private http: HttpClient,
              private documentService: DocumentService) {}

  get f(){
    return this.myForm.controls;
  }

  onFileChange(event:any) {
    
    if (event.target.files.length > 0) {
      const file = event.target.files[0];
      this.myForm.patchValue({
        fileSource: file
      });

      this.submit();
    }
  } 

  submit(){
    console.log('Submitting file');
    
    const formData = new FormData();
  
    const fileSourceValue = this.myForm.get('fileSource')?.value;
  
    if (fileSourceValue !== null && fileSourceValue !== undefined) {
        formData.append('file', fileSourceValue);
    }
       
    this.documentService.uploadDocument(formData).subscribe({
      next: res => {
        console.log(res);
			},
			error: err => console.log(err)
    });
  }

}
