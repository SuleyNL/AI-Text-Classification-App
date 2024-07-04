import { DomSanitizer } from '@angular/platform-browser'
import { PipeTransform, Pipe } from "@angular/core";

@Pipe({
  name: 'safeHtml',
  standalone: true,
})

export class SafeHtmlPipe implements PipeTransform  {
  constructor(private sanitized: DomSanitizer) {}
  transform(value: any) {
    return this.sanitized.bypassSecurityTrustHtml(value);
  }
}