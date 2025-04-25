import domain from '../../../../_globals/domain.js'

document.addEventListener('DOMContentLoaded', () => {
  const emailList = document.getElementById('emailList');
  const refreshBtn = document.getElementById('refreshEmails');

  loadEmails();

  refreshBtn.addEventListener('click', (e) => {
    e.preventDefault();
    loadEmails();
  });

  document.addEventListener('submit', async (e) => {
    if (e.target.matches('[id^="replyForm"]')) {
      e.preventDefault();
      const form = e.target;
      const submitBtn = form.querySelector('[type="submit"]');
      
      try {
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
          <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
          Sending...
        `;

        const response = await fetch(form.action, {
          method: 'POST',
          body: new FormData(form)
        });

        if (!response.ok) throw new Error('Failed to send reply');
        
        alert('Reply sent successfully!');
        bootstrap.Modal.getInstance(form.closest('.modal')).hide();
        loadEmails();
      } catch (error) {
        console.error('Error:', error);
        alert('Error sending reply');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Send Reply';
      }
    }
  });

  async function loadEmails() {
    try {
      // Show loading state
      emailList.innerHTML = `
        <div class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="sr-only">Loading...</span>
          </div>
          <p>Loading emails...</p>
        </div>
      `;

      const response = await fetch(`${domain}/msg/v1/get_emails`);
      if (!response.ok) throw new Error('Failed to fetch emails');
      
      const emails = await response.json();

      if (emails.length === 0) {
        emailList.innerHTML = `
          <div class="text-center py-4">
            <p>No emails found</p>
          </div>
        `;
        return;
      }

      emailList.innerHTML = emails.map((email, index) => `
        <div class="list-group-item list-group-item-action p-2">
          <div class="d-flex align-items-center gap-2">
            <img src="${email.sender_profile_picture || '/static/img/default_profile.png'}" 
                 alt="${email.sender}" width="40" height="40" class="rounded-circle flex-shrink-0">
            <div class="flex-grow-1 overflow-hidden" style="min-width: 0;">
              <div class="d-flex justify-content-between">
                <h6 class="mb-0 text-truncate">${escapeHtml(email.sender)}</h6>
                <small class="opacity-50 text-nowrap ps-2">${escapeHtml(email.timestamp)}</small>
              </div>
              <p class="mb-0 text-truncate"><small>${escapeHtml(email.subject)}</small></p>
              <p class="mb-0 text-truncate text-muted"><small>${escapeHtml(stripHtml(email.body))}</small></p>
            </div>
            <div class="btn-group btn-group-sm">
              <button class="btn btn-outline-primary" data-bs-toggle="modal" data-bs-target="#viewEmailModal${index}">
                <i class="fas fa-eye"></i>
              </button>
              <button class="btn btn-outline-success" data-bs-toggle="modal" data-bs-target="#replyEmailModal${index}">
                <i class="fas fa-reply"></i>
              </button>
            </div>
          </div>
        </div>

        <!-- Modal for Viewing Email -->
        <div class="modal fade" id="viewEmailModal${index}" tabindex="-1" aria-labelledby="viewEmailModalLabel${index}" aria-hidden="true">
          <div class="modal-dialog modal-lg">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="viewEmailModalLabel${index}">${escapeHtml(email.subject)}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div class="modal-body">
                <div class="d-flex align-items-center mb-3">
                  <img src="${email.sender_profile_picture || '/static/img/default_profile.png'}" 
                       alt="${escapeHtml(email.sender)}" width="50" height="50" class="rounded-circle me-2">
                  <div>
                    <p class="mb-0"><strong>From:</strong> ${escapeHtml(email.sender)}</p>
                    <p class="mb-0 text-muted"><small>${escapeHtml(email.timestamp)}</small></p>
                  </div>
                </div>
                <div class="border-top pt-3">
                  <div class="email-content">${sanitizeHtml(email.full_body)}</div>
                </div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal for Replying to Email -->
        <div class="modal fade" id="replyEmailModal${index}" tabindex="-1" aria-labelledby="replyEmailModalLabel${index}" aria-hidden="true">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="replyEmailModalLabel${index}">Reply to ${escapeHtml(email.sender)}</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div class="modal-body">
                <form id="replyForm${index}" method="POST" action="/send_reply">
                  <input type="hidden" name="email_id" value="${escapeHtml(email.id)}">
                  <input type="hidden" name="to" value="${escapeHtml(email.sender)}">
                  <input type="hidden" name="subject" value="Re: ${escapeHtml(email.subject)}">
                  <div class="form-group mb-3">
                    <label for="replyBody${index}" class="form-label">Your Reply:</label>
                    <textarea class="form-control" id="replyBody${index}" name="replyBody" rows="4" required></textarea>
                  </div>
                  <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <button type="submit" class="btn btn-primary">Send Reply</button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </div>
      `).join('');
      
    } catch (error) {
      console.error('Error loading emails:', error);
      emailList.innerHTML = `
        <div class="text-center py-4">
          <p>Error loading emails</p>
          <button class="btn btn-sm btn-primary" onclick="window.location.reload()">Retry</button>
        </div>
      `;
    }
  }

  function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe.toString()
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function stripHtml(html) {
    if (!html) return '';
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || '';
  }

  function sanitizeHtml(html) {
    if (!html) return '';
    const allowedTags = [
      'p', 'br', 'div', 'span', 'b', 'strong', 'i', 'em', 'u', 
      'ol', 'ul', 'li', 'a', 'img', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
    ];
    const allowedAttributes = {
      a: ['href', 'title', 'target'],
      img: ['src', 'alt', 'width', 'height']
    };
    
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    
    const scripts = tmp.querySelectorAll('script, style, iframe, frame, object, embed');
    scripts.forEach(script => script.remove());
    
    const allElements = tmp.querySelectorAll('*');
    allElements.forEach(el => {
      if (!allowedTags.includes(el.tagName.toLowerCase())) {
        el.outerHTML = el.innerHTML;
        return;
      }
      
      const attributes = Array.from(el.attributes);
      attributes.forEach(attr => {
        const tag = el.tagName.toLowerCase();
        if (!(allowedAttributes[tag] && allowedAttributes[tag].includes(attr.name.toLowerCase()))) {
          el.removeAttribute(attr.name);
        }
      });
      
      if (el.tagName.toLowerCase() === 'a') {
        const href = el.getAttribute('href');
        if (href && !href.startsWith('http://') && !href.startsWith('https://') && !href.startsWith('mailto:')) {
          el.removeAttribute('href');
        } else {
          el.setAttribute('target', '_blank');
          el.setAttribute('rel', 'noopener noreferrer');
        }
      }
    });
    
    return tmp.innerHTML;
  }
});