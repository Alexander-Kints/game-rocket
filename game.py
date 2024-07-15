import tkinter as tk
from tkinter import messagebox
import random


class GameField:
    def __init__(self, width, height, color, star_count):
        self.width = width
        self.height = height
        self.color = color
        self.star_count = star_count
        self.star_img = None
        self.hp_img = None


class Bullet:
    def __init__(self, speed):
        self.speed = speed
        self.id = None


class AlienBullet(Bullet):
    def move(self, canvas, master, rocket):
        coords = canvas.coords(self.id)
        if not coords:
            return
        if coords[1] > 1500:
            canvas.delete(self.id)
            return

        canvas.move(self.id, 0, self.speed)

        if check_collision(canvas, self.id, rocket.id):
            canvas.delete(self.id)
            if rocket.hp_ids:
                canvas.delete(rocket.hp_ids.pop())
            if not rocket.hp_ids:
                canvas.delete(rocket.id)
                rocket.is_alive = False
            return

        master.after(15, self.move, canvas, master, rocket)


class RocketBullet(Bullet):
    def move(self, canvas, master, alien):
        coords = canvas.coords(self.id)
        if not coords:
            return
        if coords[1] < 0:
            canvas.delete(self.id)
            return

        canvas.move(self.id, 0, -self.speed)

        if check_collision(canvas, self.id, alien.id):
            canvas.delete(self.id)
            if alien.hp_ids:
                canvas.delete(alien.hp_ids.pop())

            if not alien.hp_ids:
                canvas.delete(alien.id)
                alien.is_alive = False
            return

        master.after(15, self.move, canvas, master, alien)


class BaseObject:
    def __init__(self, img_url, bullet_img_url, speed, bullet_speed, hp):
        self.img_url = img_url
        self.bullet_img_url = bullet_img_url
        self.speed = speed
        self.bullet_speed = bullet_speed
        self.hp = hp
        self.hp_ids = []
        self.is_alive = True
        self.id = None
        self.img = None
        self.bullet_img = None


class Rocket(BaseObject):
    def create_bullet(self, canvas, master, alien):
        if not self.is_alive:
            return
        bullet = RocketBullet(self.bullet_speed)
        bullet.id = canvas.create_image(
            (canvas.coords(self.id)[0], canvas.coords(self.id)[1] - 80),
            image=self.bullet_img, anchor='center'
        )

        bullet.move(canvas, master, alien)


class Alien(BaseObject):
    flag_left = True
    flag_right = False

    def move(self, canvas, master, field):
        coords = canvas.coords(self.id)

        if not coords:
            return

        if self.flag_left:
            canvas.move(self.id, -self.speed, 0)
        elif self.flag_right:
            canvas.move(self.id, self.speed, 0)

        if self.flag_left and coords[0] < 128:
            self.flag_right = True
            self.flag_left = False
        elif self.flag_right and coords[0] > field.width - 128:
            self.flag_left = True
            self.flag_right = False

        master.after(15, self.move, canvas, master, field)

    def create_bullet(self, canvas, master, rocket):
        if not self.is_alive or not rocket.is_alive:
            canvas.delete('all')
            if messagebox.askokcancel("Игра окончена", "Начать заново?"):
                game_restart()
                return
            else:
                master.destroy()
                return

        bullet = AlienBullet(self.bullet_speed)
        bullet.id = canvas.create_image(
            (canvas.coords(self.id)[0],
             canvas.coords(self.id)[1] + 80),
            image=self.bullet_img, anchor='center'
        )

        bullet.move(canvas, master, rocket)
        master.after(1000, self.create_bullet, canvas, master, rocket)


class Game:
    def __init__(self, game_field):
        self.game_field = game_field
        self.rocket = None
        self.alien = None

        self.master = tk.Tk()
        self.canvas = tk.Canvas(
            self.master, bg=self.game_field.color,
            height=self.game_field.height, width=self.game_field.width
        )

        self.canvas.pack()
        self.master.bind("<KeyPress>", self.rocket_move)

    def set_rocket(self, rocket):
        self.rocket = rocket

    def set_alien(self, alien):
        self.alien = alien

    def paint_stars(self, img_url):
        self.game_field.star_img = tk.PhotoImage(file=img_url)
        for _ in range(self.game_field.star_count):
            coords = (random.randint(0, self.game_field.width), random.randint(0, self.game_field.height))
            self.canvas.create_image(coords, image=self.game_field.star_img, anchor='center')

    def paint_hp(self, img_url):
        self.game_field.hp_img = tk.PhotoImage(file=img_url)

        for i in range(self.rocket.hp):
            self.rocket.hp_ids.append(
                self.canvas.create_image(
                    (40 + i * 40, self.game_field.height - 40),
                    image=self.game_field.hp_img, anchor='center'
                )
            )

        for i in range(self.alien.hp):
            self.alien.hp_ids.append(
                self.canvas.create_image(
                    ((self.game_field.width - 40) - i * 40, 40),
                    image=self.game_field.hp_img, anchor='center'
                )
            )

    def paint_rocket(self):
        self.rocket.img = tk.PhotoImage(file=self.rocket.img_url)
        self.rocket.id = self.canvas.create_image(
            (self.game_field.width / 2, self.game_field.height - 100),
            image=self.rocket.img, anchor='center'
        )
        self.rocket.bullet_img = tk.PhotoImage(
            file=self.rocket.bullet_img_url
        )

    def paint_alien(self):
        self.alien.img = tk.PhotoImage(file=self.alien.img_url)
        self.alien.id = self.canvas.create_image(
            (random.randint(200, self.game_field.width - 200), 100),
            image=self.alien.img, anchor='center'
        )
        self.alien.bullet_img = tk.PhotoImage(file=self.alien.bullet_img_url)
        self.alien.move(self.canvas, self.master, self.game_field)
        self.alien.create_bullet(self.canvas, self.master, self.rocket)

    def rocket_move(self, event):
        if ((event.keysym == 'Left' or event.keysym == 'a') and
                self.canvas.coords(self.rocket.id)[0] > 60):
            self.canvas.move(self.rocket.id, -self.rocket.speed, 0)
        if ((event.keysym == 'Right' or event.keysym == 'd') and
                self.canvas.coords(self.rocket.id)[0] < self.game_field.width - 60):
            self.canvas.move(self.rocket.id, self.rocket.speed, 0)
        if event.keysym == 'space':
            self.rocket.create_bullet(self.canvas, self.master, self.alien)

    def start(self):
        self.master.mainloop()


def check_collision(canvas, item1, item2):
    bbox1 = canvas.bbox(item1)
    bbox2 = canvas.bbox(item2)
    if bbox1 and bbox2:
        return (
            bbox1[0] < bbox2[2] and
            bbox1[2] > bbox2[0] and
            bbox1[1] < bbox2[3] and
            bbox1[3] > bbox2[1]
        )
    return False


def game_restart():
    rocket = Rocket("img/rocket.png", "img/bullet.png", 15, 5, 3)
    alien = Alien("img/alien.png", "img/fireball.png", 3, 5, 10)

    game.set_rocket(rocket)
    game.set_alien(alien)

    game.paint_stars("img/star.png")

    game.paint_rocket()

    game.paint_alien()

    game.paint_hp("img/hp.png")

    game.start()


game_field = GameField(1200, 800, "#414a4c", 80)

game = Game(game_field)

game_restart()
