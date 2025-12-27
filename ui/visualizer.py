import cv2
import numpy as np

class Visualizer:
    def __init__(self, width=640, height=100):
        self.width = width
        self.height = height
        self.graph_data = [] 
        self.max_points = width
        
        # Neon Palette (BGR)
        self.NEON_GREEN = (50, 255, 50)
        self.NEON_CYAN = (255, 255, 0) # BGR: 0,255,255 is Yellow? No. B=255,G=255,R=0 is CYAN.
        self.NEON_YELLOW = (0, 255, 255)
        self.NEON_RED = (50, 50, 255)
        self.SOFT_WHITE = (240, 240, 240)
        
    def update_graph(self, value):
        self.graph_data.append(value)
        if len(self.graph_data) > self.max_points:
            self.graph_data.pop(0)

    def draw_liquid_glass_rect(self, img, pt1, pt2, color=(255, 255, 255), thickness=1, radius=20, alpha=0.2):
        """Draws a 'Liquid Glass' style rounded rectangle with background blur."""
        x1, y1 = pt1
        x2, y2 = pt2
        
        # 1. Blur the background region (Frosted Glass Effect)
        # Ensure coordinates are safely within frame
        roi = img[y1:y2, x1:x2]
        if roi.size == 0: return img
        
        # Heavy Blur
        blurred_roi = cv2.GaussianBlur(roi, (25, 25), 0)
        img[y1:y2, x1:x2] = blurred_roi
        
        # 2. Draw Rounded Overlay (Simulate Shape)
        # Create a separate overlay for alpha blending
        overlay = img.copy()
        
        # Draw filled rounded rect on overlay
        # Corners
        cv2.ellipse(overlay, (x1+radius, y1+radius), (radius, radius), 180, 0, 90, color, -1)
        cv2.ellipse(overlay, (x2-radius, y1+radius), (radius, radius), 270, 0, 90, color, -1)
        cv2.ellipse(overlay, (x2-radius, y2-radius), (radius, radius), 0, 0, 90, color, -1)
        cv2.ellipse(overlay, (x1+radius, y2-radius), (radius, radius), 90, 0, 90, color, -1)
        # Sides
        cv2.rectangle(overlay, (x1+radius, y1), (x2-radius, y2), color, -1)
        cv2.rectangle(overlay, (x1, y1+radius), (x2, y2-radius), color, -1)
        
        # Blend overlay (Tint)
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
        
        # 3. Draw Border (Specular Highlight)
        border_color = (255, 255, 255) # White highlight
        # Top-Left Arc
        cv2.ellipse(img, (x1+radius, y1+radius), (radius, radius), 180, 0, 90, border_color, thickness)
        cv2.ellipse(img, (x2-radius, y1+radius), (radius, radius), 270, 0, 90, border_color, thickness)
        cv2.ellipse(img, (x2-radius, y2-radius), (radius, radius), 0, 0, 90, border_color, thickness)
        cv2.ellipse(img, (x1+radius, y2-radius), (radius, radius), 90, 0, 90, border_color, thickness)
        
        cv2.line(img, (x1+radius, y1), (x2-radius, y1), border_color, thickness)
        cv2.line(img, (x2, y1+radius), (x2, y2-radius), border_color, thickness)
        cv2.line(img, (x2-radius, y2), (x1+radius, y2), border_color, thickness)
        cv2.line(img, (x1, y2-radius), (x1, y1+radius), border_color, thickness)
        
        return img
            
    def draw(self, frame, metrics):
        # 1. Liquid Glass Status Box
        box_w = 230
        box_h = 240
        self.draw_liquid_glass_rect(frame, (10, 40), (10+box_w, 40+box_h), color=(50, 50, 50), alpha=0.3)
        
        # 2. Draw Metrics
        x = 25
        y = 75
        
        status = metrics.get("Status", "Init")
        cv2.putText(frame, f"STATUS: {status}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.NEON_GREEN, 2)
        y += 30
        
        for key, val in metrics.items():
            if key == "Status" or "Rate" in key: continue 
            
            color = self.SOFT_WHITE
            if key == "ALERT": color = self.NEON_RED
            
            label = f"{key}: {val}"
            # Shadow effect for text readability
            cv2.putText(frame, label, (x+1, y+1), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0,0,0), 1, cv2.LINE_AA)
            cv2.putText(frame, label, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)
            y += 25
            
        # 3. Scrolling Graph (Bottom)
        graph_h = 80
        # Draw background bar for graph
        cv2.rectangle(frame, (0, frame.shape[0]-graph_h), (self.width, frame.shape[0]), (10, 10, 10), -1)
        # Apply slight blur to blend
        
        graph_img = np.zeros((graph_h, self.width, 3), dtype=np.uint8)
        
        if len(self.graph_data) > 1:
            min_val = min(self.graph_data)
            max_val = max(self.graph_data)
            
            if(max_val == min_val): max_val += 1e-5
            
            normalized = [
                    int(graph_h - (v - min_val) / (max_val - min_val) * (graph_h - 10) - 5) 
                    for v in self.graph_data
                ]
            
            # Draw Polyline for smoother look
            pts = np.array([ [i, normalized[i]] for i in range(len(normalized)) ], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(graph_img, [pts], False, self.NEON_GREEN, 1, cv2.LINE_AA)

        # Overlay graph with transparency
        roi = frame[-graph_h:, :self.width]
        masked_graph = cv2.addWeighted(roi, 1.0, graph_img, 0.8, 0)
        frame[-graph_h:, :self.width] = masked_graph
        
        cv2.putText(frame, "Digital Pulse", (10, frame.shape[0]-graph_h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.NEON_YELLOW, 1, cv2.LINE_AA)
        
        return frame
