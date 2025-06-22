type NotificationType = "success" | "error" | "warning" | "info";

interface NotificationOptions {
  title: string;
  description?: string;
  type?: NotificationType;
  duration?: number;
  showCloseButton?: boolean;
}

class NotificationManager {
  private container: HTMLDivElement | null = null;
  private notifications: Map<string, HTMLDivElement> = new Map();
  private resizeListener: (() => void) | null = null;
  private resizeTimeout: number | null = null;

  constructor() {
    // Create the resize handler
    this.resizeListener = this.handleResize.bind(this);

    // Add resize listener when window exists (for SSR compatibility)
    if (typeof window !== "undefined") {
      window.addEventListener("resize", this.resizeListener);
    }
  }

  // Handle window resize events with debouncing
  private handleResize() {
    if (this.resizeTimeout) {
      window.clearTimeout(this.resizeTimeout);
    }

    this.resizeTimeout = window.setTimeout(() => {
      this.updateContainerPosition();
    }, 150); // Debounce for performance
  }

  // Update container position based on current viewport size
  private updateContainerPosition() {
    if (!this.container) return;

    const isMobile = window.innerWidth <= 640;

    this.container.style.top = isMobile ? "10px" : "20px";
    this.container.style.right = isMobile ? "10px" : "20px";
    this.container.style.left = isMobile ? "10px" : "auto";
    this.container.style.maxWidth = isMobile ? "none" : "400px";
    this.container.style.width = isMobile ? "auto" : "";
  }

  private createContainer() {
    if (!this.container) {
      this.container = document.createElement("div");
      this.container.id = "notification-container";

      // Base container styles (non-responsive)
      this.container.style.position = "fixed";
      this.container.style.zIndex = "9999";
      this.container.style.pointerEvents = "none";

      // Set responsive positioning
      this.updateContainerPosition();

      document.body.appendChild(this.container);
    }
    return this.container;
  }

  private getTypeStyles(type: NotificationType) {
    const styles = {
      success: {
        bg: "#10b981",
        border: "#059669",
        icon: "✓",
      },
      error: {
        bg: "#ef4444",
        border: "#dc2626",
        icon: "✕",
      },
      warning: {
        bg: "#f59e0b",
        border: "#d97706",
        icon: "⚠",
      },
      info: {
        bg: "#3b82f6",
        border: "#2563eb",
        icon: "ℹ",
      },
    };
    return styles[type] || styles.info;
  }

  show(options: NotificationOptions) {
    const {
      title,
      description,
      type = "info",
      duration = 3000,
      showCloseButton = true,
    } = options;

    const container = this.createContainer();
    const id = Date.now().toString();
    const typeStyles = this.getTypeStyles(type);

    // Check if mobile viewport
    const isMobile = window.innerWidth <= 640;

    // Create notification element
    const notification = document.createElement("div");
    notification.style.cssText = `
      background: white;
      border-left: 4px solid ${typeStyles.border};
      border-radius: 8px;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
      margin-bottom: 12px;
      padding: 16px;
      pointer-events: auto;
      transform: translateX(100%);
      transition: all 0.3s ease-in-out;
      opacity: 0;
      word-wrap: break-word;
      ${isMobile ? "width: 100%; max-width: none;" : "max-width: 400px;"}
    `;

    notification.innerHTML = `
      <div style="display: flex; align-items: flex-start; gap: 12px;">
        <div style="
          background: ${typeStyles.bg};
          color: white;
          border-radius: 50%;
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 12px;
          font-weight: bold;
          flex-shrink: 0;
        ">
          ${typeStyles.icon}
        </div>
        <div style="flex: 1; min-width: 0;">
          <div style="font-weight: 600; color: #1f2937; margin-bottom: 4px; font-size: ${isMobile ? "13px" : "14px"};">
            ${title}
          </div>
          ${
            description
              ? `
            <div style="color: #6b7280; font-size: ${isMobile ? "12px" : "13px"}; line-height: 1.4;">
              ${description}
            </div>
          `
              : ""
          }
        </div>
        ${
          showCloseButton
            ? `
          <button 
            onclick="window.notificationManager.remove('${id}')"
            style="
              background: none;
              border: none;
              color: #9ca3af;
              cursor: pointer;
              font-size: 18px;
              line-height: 1;
              padding: 0;
              margin-left: 8px;
              flex-shrink: 0;
            "
            onmouseover="this.style.color='#374151'"
            onmouseout="this.style.color='#9ca3af'"
          >
            ×
          </button>
        `
            : ""
        }
      </div>
    `;

    // Add to container and store reference
    container.appendChild(notification);
    this.notifications.set(id, notification);

    // Animate in
    requestAnimationFrame(() => {
      notification.style.transform = "translateX(0)";
      notification.style.opacity = "1";
    });

    // Auto remove after duration
    if (duration > 0) {
      setTimeout(() => {
        this.remove(id);
      }, duration);
    }

    return id;
  }

  remove(id: string) {
    const notification = this.notifications.get(id);
    if (notification) {
      notification.style.transform = "translateX(100%)";
      notification.style.opacity = "0";

      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
        this.notifications.delete(id);
      }, 300);
    }
  }

  // Clean up resources when the app is unmounted
  destroy() {
    // Remove resize listener
    if (typeof window !== "undefined" && this.resizeListener) {
      window.removeEventListener("resize", this.resizeListener);
    }

    // Clear timeout if exists
    if (this.resizeTimeout) {
      window.clearTimeout(this.resizeTimeout);
      this.resizeTimeout = null;
    }

    // Remove container and reset state
    if (this.container && this.container.parentNode) {
      this.container.parentNode.removeChild(this.container);
    }
    this.container = null;
    this.notifications.clear();
  }

  success(title: string, description?: string) {
    return this.show({ title, description, type: "success" });
  }

  error(title: string, description?: string) {
    return this.show({ title, description, type: "error" });
  }

  warning(title: string, description?: string) {
    return this.show({ title, description, type: "warning" });
  }

  info(title: string, description?: string) {
    return this.show({ title, description, type: "info" });
  }
}

// Create global instance
const notificationManager = new NotificationManager();

// Make it available globally for close button
declare global {
  interface Window {
    notificationManager: NotificationManager;
  }
}

window.notificationManager = notificationManager;

// Export the toast object with correct method signatures
export const toast = {
  success: (title: string, options?: { description?: string }) =>
    notificationManager.success(title, options?.description),

  error: (title: string, options?: { description?: string }) =>
    notificationManager.error(title, options?.description),

  warning: (title: string, options?: { description?: string }) =>
    notificationManager.warning(title, options?.description),

  info: (title: string, options?: { description?: string }) =>
    notificationManager.info(title, options?.description),
};

export default toast;
