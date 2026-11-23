import os, math, tkinter as tk
from PIL import Image, ImageDraw

class Skin3DViewer(tk.Canvas):
    def __init__(self, parent, width=175, height=235, **kwargs):
        super().__init__(parent, width=width, height=height, bg=kwargs.pop("bg","#131a16"), highlightthickness=0, **kwargs)
        self.w, self.h = width, height
        self.yaw, self.pitch, self.hy, self.hp = -0.35, 0.12, 0.0, 0.0
        self.dx = self.dy = None
        self.skin_img = self._default_skin()
        self.bind("<ButtonPress-1>", lambda e: setattr(self, "dx", e.x) or setattr(self, "dy", e.y))
        self.bind("<B1-Motion>", self._drag)
        self.winfo_toplevel().bind_all("<Motion>", self._hover, add="+")
        self.after(30, self.render)

    def _default_skin(self):
        im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        dr.rectangle((8, 8, 15, 15), fill="#c69c72")
        dr.rectangle((0, 8, 7, 15), fill="#b58960"); dr.rectangle((16, 8, 23, 15), fill="#b58960")
        dr.rectangle((8, 0, 15, 7), fill="#3b2618"); dr.rectangle((24, 8, 31, 15), fill="#3b2618")
        dr.rectangle((8, 8, 15, 9), fill="#3b2618")
        dr.point((9, 11), fill="#fff"); dr.point((10, 11), fill="#4b369d")
        dr.point((13, 11), fill="#4b369d"); dr.point((14, 11), fill="#fff")
        dr.rectangle((10, 13, 13, 14), fill="#8c5840")
        dr.rectangle((16, 20, 39, 31), fill="#00a8a8")
        dr.rectangle((40, 20, 55, 31), fill="#c69c72"); dr.rectangle((32, 52, 47, 63), fill="#c69c72")
        dr.rectangle((0, 20, 15, 31), fill="#334499"); dr.rectangle((16, 52, 31, 63), fill="#2c3b85")
        return im

    def set_skin(self, path):
        if path and os.path.exists(path):
            im = Image.open(path).convert("RGBA")
            if im.size == (64, 32):
                im64 = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
                im64.paste(im, (0, 0)); im = im64
            self.skin_img = im
            self.render()

    load_skin = update_skin = render_skin = set_skin

    def _drag(self, e):
        if self.dx is not None:
            self.yaw -= (e.x - self.dx) * 0.015
            self.pitch = max(-0.6, min(0.6, self.pitch - (e.y - self.dy) * 0.01))
            self.dx, self.dy = e.x, e.y
            self.render()

    def _hover(self, e):
        if not self.winfo_exists():
            return
        cx = self.winfo_rootx() + self.w / 2.0
        cy = self.winfo_rooty() + self.h * 0.25
        self.hy = max(-0.65, min(0.65, -((e.x_root - cx) / 320.0) * 0.55))
        self.hp = max(-0.45, min(0.45, -((e.y_root - cy) / 240.0) * 0.40))
        self.render()

    def _rot(self, x, y, z, yaw, pitch):
        cy, sy = math.cos(yaw), math.sin(yaw)
        x1, z1 = x * cy - z * sy, x * sy + z * cy
        cp, sp = math.cos(pitch), math.sin(pitch)
        return x1, y * cp - z1 * sp, y * sp + z1 * cp

    def _box(self, polys, sz, off, piv, uvs, hy=0.0, hp=0.0, inf=0.0, tint=1.0):
        bw, bh, bd = sz
        sx, sy, sz_h = (bw + inf) / 2.0, (bh + inf) / 2.0, (bd + inf) / 2.0
        ox, oy, oz = off; px, py, pz = piv
        verts = (
            (-sx,-sy,-sz_h), (sx,-sy,-sz_h), (sx,sy,-sz_h), (-sx,sy,-sz_h),
            (-sx,-sy,sz_h),  (sx,-sy,sz_h),  (sx,sy,sz_h),  (-sx,sy,sz_h)
        )
        proj, sc, cx, cy = [], 6.8, self.w / 2.0, self.h * 0.49
        for vx, vy, vz in verts:
            lx, ly, lz = vx + ox - px, vy + oy - py, vz + oz - pz
            if hy or hp: lx, ly, lz = self._rot(lx, ly, lz, hy, hp)
            rx, ry, rz = self._rot(lx + px, ly + py, lz + pz, self.yaw, self.pitch)
            p = 1.0 - rz * 0.012
            proj.append((cx + rx * sc * p, cy + ry * sc * p, rz))

        v0, v1, v2, v3, v4, v5, v6, v7 = proj
        faces = (
            ((v4, v5, v6, v7), uvs.get("front"), 1.00),
            ((v1, v0, v3, v2), uvs.get("back"),  0.80),
            ((v0, v4, v7, v3), uvs.get("left"),  0.88),
            ((v5, v1, v2, v6), uvs.get("right"), 0.88),
            ((v0, v1, v5, v4), uvs.get("top"),   1.05),
            ((v7, v6, v2, v3), uvs.get("bot"),   0.70),
        )
        for (p0, p1, p2, p3), uv_rect, sh in faces:
            p0x, p0y, p0z = p0
            p1x, p1y, p1z = p1
            p2x, p2y, p2z = p2
            p3x, p3y, p3z = p3
            if (p1x - p0x) * (p2y - p0y) - (p1y - p0y) * (p2x - p0x) <= 0:
                continue
            u0, v0_uv, uw, vh = uv_rect
            has_pixels = False
            for gx in range(uw):
                t0x, t1x = gx / uw, (gx + 1) / uw
                for gy in range(vh):
                    r, g, b, a = self.skin_img.getpixel((u0 + gx, v0_uv + gy))
                    if a < 30:
                        continue
                    has_pixels = True
                    t0y, t1y = gy / vh, (gy + 1) / vh
                    def ip(tx, ty):
                        tx0 = p0x + (p1x - p0x) * tx; ty0 = p0y + (p1y - p0y) * tx
                        bx0 = p3x + (p2x - p3x) * tx; by0 = p3y + (p2y - p3y) * tx
                        return (tx0 + (bx0 - tx0) * ty, ty0 + (by0 - ty0) * ty)
                    q0x, q0y = ip(t0x, t0y)
                    q1x, q1y = ip(t1x, t0y)
                    q2x, q2y = ip(t1x, t1y)
                    q3x, q3y = ip(t0x, t1y)
                    col = f"#{min(255,int(r*sh*tint)):02x}{min(255,int(g*sh*tint)):02x}{min(255,int(b*sh*tint)):02x}"
                    az = (p0z + p1z + p2z + p3z) / 4.0 + (0.05 if inf > 0 else 0.0)
                    polys.append((az, (q0x, q0y, q1x, q1y, q2x, q2y, q3x, q3y), col, ""))
            if has_pixels and inf == 0:
                az_edge = (p0z + p1z + p2z + p3z) / 4.0 - 0.01
                polys.append((az_edge, (p0x, p0y, p1x, p1y, p2x, p2y, p3x, p3y), "", "#cccccc"))

    def render(self):
        self.delete("all")
        polys = []
        self._box(polys, (8,8,8), (0,-10,0), (0,-6,0), {"front":(8,8,8,8),"back":(24,8,8,8),"left":(0,8,8,8),"right":(16,8,8,8),"top":(8,0,8,8),"bot":(16,0,8,8)}, self.hy, self.hp, 0.0, 1.00)
        self._box(polys, (8,8,8), (0,-10,0), (0,-6,0), {"front":(40,8,8,8),"back":(56,8,8,8),"left":(32,8,8,8),"right":(48,8,8,8),"top":(40,0,8,8),"bot":(48,0,8,8)}, self.hy, self.hp, 0.55, 1.00)
        self._box(polys, (8,12,4), (0,0,0), (0,0,0), {"front":(20,20,8,12),"back":(32,20,8,12),"left":(16,20,4,12),"right":(28,20,4,12),"top":(20,16,8,4),"bot":(28,16,8,4)}, 0.0, 0.0, 0.0, 0.94)
        self._box(polys, (4,12,4), (-6,0,0), (-6,-4,0), {"front":(44,20,4,12),"back":(52,20,4,12),"left":(40,20,4,12),"right":(48,20,4,12),"top":(44,16,4,4),"bot":(48,16,4,4)}, 0.0, 0.0, 0.0, 0.88)
        self._box(polys, (4,12,4), (6,0,0), (6,-4,0), {"front":(36,52,4,12),"back":(44,52,4,12),"left":(32,52,4,12),"right":(40,52,4,12),"top":(36,48,4,4),"bot":(40,48,4,4)}, 0.0, 0.0, 0.0, 0.88)
        self._box(polys, (4,12,4), (-2,12,0), (-2,6,0), {"front":(4,20,4,12),"back":(12,20,4,12),"left":(0,20,4,12),"right":(8,20,4,12),"top":(4,16,4,4),"bot":(8,16,4,4)}, 0.0, 0.0, 0.0, 0.83)
        self._box(polys, (4,12,4), (2,12,0), (2,6,0), {"front":(20,52,4,12),"back":(28,52,4,12),"left":(16,52,4,12),"right":(24,52,4,12),"top":(20,48,4,4),"bot":(24,48,4,4)}, 0.0, 0.0, 0.0, 0.83)
        polys.sort(key=lambda item: item[0], reverse=True)
        for _, pts, col, outl in polys:
            self.create_polygon(pts, fill=col, outline=outl)
