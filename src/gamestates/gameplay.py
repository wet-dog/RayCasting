import pygame
import math
from gamestates.gamestate import GameState
from client import Client
from vector import Vector


class Gameplay(GameState):
    def __init__(self):
        super(Gameplay, self).__init__()
        self.next_state = "MENU"

        self.dir = Vector(-1, 0)
        self.plane = Vector(0, 0.66)

        self.moveSpeed = 5.0
        self.rotSpeed = 3.0

    def startup(self, persistent):
        super().startup(persistent)
        self.worldMap = self.persist["map"]
        self.spawn_point = self.persist["spawn_point"]
        self.pos = Vector(self.spawn_point[0], self.spawn_point[1])

        # If the game is in multiplayer mode then set the position of a player
        # 2 and create a client instance.
        if self.persist["multi_flag"]:
            self.player2_pos = Vector(15, 15)
            self.client = Client()
            # Message to be sent to the other player.
            self.message = {"client id": self.client.id, "pos": self.player2_pos,
                            "map": self.worldMap}

        # Hide the mouse cursor as it is not needed in gameplay.
        pygame.mouse.set_visible(False)

    def update(self, dt):
        # Print FPS
        # print(dt)
        dt /= 1000
        # moveSpeed and rotSpeed are * dt so the player doesn't move/ turn
        # faster/ slower when the game's framerate increases/ decreases.
        self.moveSpeed = dt * 5    # squares/ second
        self.rotSpeed = dt * 3     # radians/ second

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.done = True

        if keys[pygame.K_w]:
            # Move forward in the direction the player is facing by a certain
            # amount (moveSpeed).
            # int() to round pos and index 2D array correctly
            newPos = (self.pos + self.dir*self.moveSpeed)
            # If statements check if where the player is moving to is empty.
            if self.worldMap[int(newPos.x)][int(self.pos.y)] <= 0:
                self.pos.x = newPos.x
            if self.worldMap[int(self.pos.x)][int(newPos.y)] <= 0:
                self.pos.y = newPos.y

        if keys[pygame.K_s]:
            # Move backward in the opposite direction the player is facing by
            # a certain amount (moveSpeed).
            # int() to round pos and index 2D array correctly
            newPos = (self.pos - self.dir*self.moveSpeed)
            # If statements check if where the player is moving to is empty.
            if self.worldMap[int(newPos.x)][int(self.pos.y)] <= 0:
                self.pos.x = newPos.x
            if self.worldMap[int(self.pos.x)][int(newPos.y)] <= 0:
                self.pos.y = newPos.y

        if keys[pygame.K_d]:
            # Direction of the player and plane vector rotated by multiplying
            # their x and y components by the rotation matrix:
            # [ cos(Θ) -sin(Θ) ]
            # [ sin(Θ)  cos(Θ) ]
            # Where Θ is the angle to rotate by.
            # Θ = -rotSpeed
            # self.rotSpeed is made negative in order to rotate to the right.

            self.dir.x, self.dir.y = (
                (self.dir.x*math.cos(-self.rotSpeed)
                 - self.dir.y*math.sin(-self.rotSpeed)),
                (self.dir.x*math.sin(-self.rotSpeed)
                 + self.dir.y*math.cos(-self.rotSpeed))
                )

            self.plane.x, self.plane.y = (
                (self.plane.x*math.cos(-self.rotSpeed)
                 - self.plane.y*math.sin(-self.rotSpeed)),
                (self.plane.x*math.sin(-self.rotSpeed)
                 + self.plane.y*math.cos(-self.rotSpeed))
            )

        if keys[pygame.K_a]:
            # Direction of the player and plane vector rotated by multiplying
            # their x and y components by the rotation matrix:
            # [ cos(Θ) -sin(Θ) ]
            # [ sin(Θ)  cos(Θ) ]
            # Where Θ is the angle to rotate by.
            # Θ = rotSpeed
            # self.rotSpeed is left positive in order to rotate to the left.

            self.dir.x, self.dir.y = (
                (self.dir.x*math.cos(self.rotSpeed)
                 - self.dir.y*math.sin(self.rotSpeed)),
                (self.dir.x*math.sin(self.rotSpeed)
                 + self.dir.y*math.cos(self.rotSpeed))
                )

            self.plane.x, self.plane.y = (
                (self.plane.x*math.cos(self.rotSpeed)
                 - self.plane.y*math.sin(self.rotSpeed)),
                (self.plane.x*math.sin(self.rotSpeed)
                 + self.plane.y*math.cos(self.rotSpeed))
            )

        # If in multiplayer mode.
        if self.persist["multi_flag"]:
            # Change the pos sent in the message to the current player position.
            self.message["pos"] = self.pos
            # Send the other player the message (client ID, pos, map)
            self.client.send(self.message)
            # Receive the message from the other player.
            received = self.client.receive()
            # If the other client is player 1 then use their map.
            other_client_id = received["client id"]
            if other_client_id < self.client.id:
                self.worldMap = received["map"]
            # Set player 2's position to the position player 2 has sent.
            self.player2_pos = received["pos"]

    def draw(self, surface):
        """Raycasting rendering algorithm of the game."""
        surface.fill(pygame.Color("black"))

        # List to keep track of the distance from the player to drawn stripes
        # of walls.
        ZBuffer = []

        w = surface.get_width()
        h = surface.get_height()
        # For every x pixel of the screen.
        for x in range(w):
            # Convert the x coord of the screen to x coord of the camera plane
            # So instead of  0 --> 360 --> 720
            # it is         -1 --> 0 --> 1
            cameraX = (2*x / w) - 1
            # Stop zero division error.
            cameraX += 0.001
            # Find the ray direction using vector maths.
            rayDir = self.dir + self.plane*cameraX

            # Convert player pos (float) to map pos (int).
            mapPos = Vector(self.pos.x, self.pos.y)
            mapPos = mapPos.round()

            sideDistX = 0
            sideDistY = 0

            deltaDistX = abs(1 / rayDir.x)
            deltaDistY = abs(1 / rayDir.y)

            perpWallDist = 0

            stepX = 0
            stepY = 0

            hit = 0
            side = 0

            # If the ray is pointing to the left.
            if rayDir.x < 0:
                # Step to the left.
                stepX = -1
                # Straight line distance from player to first x-side
                # pos.x - mapPos.x to find x-component of distance
                # * deltaDistX to find the straight line distance
                sideDistX = (self.pos.x - mapPos.x) * deltaDistX
            # If the ray is pointing to the right.
            else:
                # Step to the right.
                stepX = 1
                # Straight line distance from player to first x-side
                # mapPos.x + 1 - pos.x to find x-component of distance
                # mapPos is pos rounded down - but it needs to be rounded up
                # to work out the difference - so +1
                # * deltaDistX to find the straight line distance
                sideDistX = (mapPos.x + 1 - self.pos.x) * deltaDistX

            # If ray is pointing down.
            if rayDir.y < 0:
                # Step down.
                stepY = -1
                # Straight line distance from player to first y-side
                # pos.y - mapPos.y to find y-component of distance
                # * deltaDistY to find the straight line distance
                sideDistY = (self.pos.y - mapPos.y) * deltaDistY
            # If ray is pointing up.
            else:
                # Step up.
                stepY = 1
                # Straight line distance from player to first y-side
                # mapPos.y + 1 - pos.y to find y-component of distance
                # mapPos is pos rounded down - but it needs to be rounded up
                # to work out the difference - so +1
                # * deltaDistY to find the straight line distance
                sideDistY = (mapPos.y + 1 - self.pos.y) * deltaDistY

            while hit == 0:
                # Modified DDA algorithm.
                # Move the ray a certain amount in either the X or Y direction
                # depending on which direction has already been travelled the
                # furthest in.
                # If the ray has moved less in the X direction then move in the
                # X direction and the same for the Y direction.
                if sideDistX < sideDistY:
                    sideDistX += deltaDistX
                    mapPos.x += stepX
                    side = 0    # X side hit
                else:
                    sideDistY += deltaDistY
                    mapPos.y += stepY
                    side = 1    # Y side hit

                # If the where the ray is isn't empty then set hit to 1.
                if self.worldMap[mapPos.x][mapPos.y] >= 1:
                    hit = 1

            # if the X side of a wall is hit
            if side == 0:
                # Find x component of distance from player to wall
                x_component = mapPos.x - self.pos.x
                # If ray stepped to the left then correct distance by +1
                # this is due to how int() always rounds down when finding
                # mapPos.x
                if stepX == -1:
                    x_component += 1
                # x component is / rayDir.x due to similar triangles and
                # simultaneous equations that solve for perpWallDist
                perpWallDist = x_component / rayDir.x
            # if the Y side of a wall is hit
            else:
                # Find y component of distance from player to wall
                y_component = mapPos.y - self.pos.y
                # If ray stepped down then correct distance by +1
                # this is due to how int() always rounds down when finding
                # mapPos.y
                if stepY == -1:
                    y_component += 1
                # y component is / rayDir.y due to similar triangles and
                # simultaneous equations that solve for perpWallDist
                perpWallDist = y_component / rayDir.y

            perpWallDist += 0.001   # stop zero division error

            lineHeight = int(h / perpWallDist)

            # if above top of screen
            drawStart = -lineHeight / 2 + h / 2
            if drawStart < 0:
                drawStart = 0

            # if below bottom of screen
            drawEnd = lineHeight / 2 + h / 2
            if drawEnd >= h:
                drawEnd = h - 1

            wallColour = pygame.Color("red")
            pygame.draw.line(surface, wallColour, (x, drawStart), (x, drawEnd))

            ZBuffer.append(perpWallDist)

        # If in multiplayer mode draw a sprite for player 2.
        if self.persist["multi_flag"]:
            # WORLD SPACE
            # Find relative position of the sprite.
            sprite = self.player2_pos - self.pos

            # stop zero division error
            if sprite.x == 0:
                sprite.x += 0.001
            if sprite.y == 0:
                sprite.y += 0.001

            # CAMERA SPACE
            # Inverse the camera matrix to get a view matrix
            invDet = 1 / (self.plane.x*self.dir.y - self.dir.x*self.plane.y)

            # X coord - in camera space
            transformX = invDet * (self.dir.y*sprite.x - self.dir.x*sprite.y)
            # Y coord - in camera space
            transformY = invDet * (-self.plane.y*sprite.x + self.plane.x*sprite.y)

            # VIEWPORT SPACE (camera plane coords)
            # cameraPlaneCoord = transformX / transformY
            # SCREEN SPACE (pixels)
            # (w / 2) * (1 + cameraPlaneCoord) - translating and scaling the
            # camera plane coords -1 -> 0 --> 1
            # to pixels coords 0 --> 640 --> 1280
            spriteScreenX = int((w / 2) * (1 + transformX / transformY))

            spriteWidth = abs(int(h / transformY))
            spriteHeight = abs(int(h / transformY))

            # Find start and end draw points for the sprite from its centre
            # (spriteScreenX).
            drawStartX = -spriteWidth / 2 + spriteScreenX
            # If drawStartX is beyond the left of the screen set drawStartX to
            # the left of the screen
            if drawStartX < 0:
                drawStartX = 0

            # If drawEndX is beyond the right of the screen set drawEndX to
            # the right of the screen
            drawEndX = spriteWidth / 2 + spriteScreenX
            if drawEndX >= w:
                drawEndX = w - 1

            # If drawStartY is beyond the top of the screen set drawStartY to
            # the top of the screen
            drawStartY = -spriteHeight / 2 + h / 2
            if drawStartY < 0:
                drawStartY = 0

            # If drawEndY is beyond the bottom of the screen set drawEndY to
            # the bottom of the screen
            drawEndY = spriteHeight / 2 + h / 2
            if drawEndY >= h:
                drawEndY = h - 1

            drawStartX = int(drawStartX)
            drawEndX = int(drawEndX)
            drawStartY = int(drawStartY)
            drawEndY = int(drawEndY)
            for stripe in range(drawStartX, drawEndX):
                # transformY > 0 check if infront of the camera
                infront_camera = transformY > 0
                # transformY < ZBuffer[stripe] check if stripe is infront of a wall
                # if the distance to the sprite is less than the wall then
                # the sprite is infront.
                infront_wall = transformY < ZBuffer[stripe]

                if infront_camera and infront_wall:
                    pygame.draw.line(surface, (0, 255, 0), (stripe, drawStartY),
                                     (stripe, drawEndY))
