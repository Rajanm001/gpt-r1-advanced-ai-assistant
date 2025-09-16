import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  
  const now = new Date();
  const diffInMinutes = Math.floor((now.getTime() - dateObj.getTime()) / (1000 * 60));
  
  if (diffInMinutes < 1) {
    return 'Just now';
  } else if (diffInMinutes < 60) {
    return `${diffInMinutes}m ago`;
  } else if (diffInMinutes < 1440) {
    const hours = Math.floor(diffInMinutes / 60);
    return `${hours}h ago`;
  } else {
    const days = Math.floor(diffInMinutes / 1440);
    return `${days}d ago`;
  }
}

export function generateConversationTitle(message: string): string {
  // Take first 50 characters and clean it up
  const cleanMessage = message.trim().replace(/\n/g, ' ');
  if (cleanMessage.length <= 50) {
    return cleanMessage;
  }
  return cleanMessage.substring(0, 47) + '...';
}

export function scrollToBottom(element: HTMLElement | null, smooth: boolean = true): void {
  if (element) {
    element.scrollTo({
      top: element.scrollHeight,
      behavior: smooth ? 'smooth' : 'auto'
    });
  }
}

export function copyToClipboard(text: string): Promise<void> {
  return navigator.clipboard.writeText(text);
}

export function downloadAsFile(content: string, filename: string, type: string = 'text/plain'): void {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}