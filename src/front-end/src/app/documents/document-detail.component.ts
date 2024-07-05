import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { DocumentService } from './document.service';
import { Subscription } from 'rxjs';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { DomSanitizer } from '@angular/platform-browser';
import document from '../../api/documents/single_document.json';

@Component({
  selector: 'app-document-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './document-detail.component.html',
  styleUrl: './document-detail.component.scss'
})
export class DocumentDetailComponent implements OnInit, OnDestroy  {
  sub!: Subscription;

  constructor(private route: ActivatedRoute,
              private documentService: DocumentService,
              private sanitizer: DomSanitizer) {}

  document: any = {};
  trustedHtml: any = '';

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    
    this.sub = this.documentService.getDocument(id).subscribe({
      next: document => {
				// this.document = document;
        console.log(document);
        
			},
			error: err => console.log(err)
    })
    this.document = document;
    this.trustedHtml = this.sanitizer.bypassSecurityTrustHtml(this.document.html);
  }

  ngOnDestroy(): void {
		this.sub.unsubscribe();
	}
}
