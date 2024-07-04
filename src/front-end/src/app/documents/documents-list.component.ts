import { Component, OnDestroy, OnInit } from '@angular/core';
import { DocumentService } from './document.service';
import { Subscription } from 'rxjs';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import snippets from '../../api/documents/snippets.json';
import { SafeHtmlPipe } from '../shared/safeHtml.pipe'

@Component({
  selector: 'app-documents-list',
  standalone: true,
  imports: [CommonModule, RouterModule, SafeHtmlPipe],
  templateUrl: './documents-list.component.html',
  styleUrl: './documents-list.component.scss'
})
export class DocumentsListComponent implements OnInit, OnDestroy {
  sub!: Subscription;

  constructor(private documentService: DocumentService) {}

  snippets: any = [];

  ngOnInit(): void {
    // this.sub = this.documentService.getDocuments().subscribe({
    //   next: documents => {
		// 		this.documents = documents;
    //     console.log(documents);
        
		// 	},
		// 	error: err => console.log(err)
    // })
    this.snippets = snippets;
  }

  ngOnDestroy(): void {
		// this.sub.unsubscribe();
	}
}
