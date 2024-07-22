import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, catchError, tap, throwError, map } from "rxjs";


@Injectable({
  providedIn: 'root'
})
export class DocumentService {
	private host = `http://127.0.0.1:8001`;
  private categoriesUrl = 'categories/1';
  private snippetsUrl = 'categories/1';
  private documentUrl = 'docs';
  private uploadUrl = 'upload';

  constructor(private http: HttpClient) { }
  // GET request to fetch Categories linked to person id
  // Query variable: person id
  getCategories(): Observable<any> {
		return this.http.get(`${this.host}/${this.categoriesUrl}`)
		.pipe(
			tap(data => console.log('All', JSON.stringify(data))),
			catchError(this.handleError)
		);
	}

	// GET request to fetch all snippets linked to person id and category id
	// Query variable: person id, category id
	getSnippets(cat_id: Number): Observable<any> {
		return this.http.get(`${this.host}/${this.snippetsUrl}/${cat_id}`)
    .pipe(
			tap(data => console.log('All', JSON.stringify(data))),
			catchError(this.handleError)
		);
	}

  getDocument(doc_id: any): Observable<any> {
		return this.http.get(`${this.host}/${this.documentUrl}/${doc_id}`)
    .pipe(
			tap(data => console.log('All', JSON.stringify(data))),
			catchError(this.handleError)
		);
	}

	uploadDocument(formData: any) {
    return this.http.post(`${this.host}/${this.uploadUrl}`, formData)
		.pipe(
			tap(res => console.log(JSON.stringify(res))),
			catchError(this.handleError)
		);
	}

  private handleError(err: HttpErrorResponse) {
		let errorMessage = '';
		if (err.error instanceof ErrorEvent) {
			errorMessage = `An error occurred: ${err.error.message}`;
		} else {
			errorMessage = `Server returned code: ${err.status}, error message is: ${err.message}`
		}
		console.log(errorMessage);
		return throwError(()=>errorMessage)
	}
}
