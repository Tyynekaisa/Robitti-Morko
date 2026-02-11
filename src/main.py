##################################################
# Robitti ja mörkö                               #
# Author: Kaisa Juhola                           #
# 11.2.2026                                      #
##################################################

import pygame
import random

class Robitti:
    def __init__(self):
        pygame.init()
        
        # Näyttö
        self.korkeus = 480
        self.leveys = 1280
        self.naytto = pygame.display.set_mode((self.leveys, self.korkeus))
        pygame.display.set_caption("Robitti ja Mörkö")

        # Robotti / pelaaja
        self.robo = pygame.image.load("robo.png")
        self.x = 20
        self.y = 380-self.robo.get_height()
        self.y_nopeus = 0
        self.maassa = True
        self.oikealle = False
        self.vasemmalle = False

        # Mörkö / vihollinen
        self.morko = pygame.image.load("hirvio.png")
        self.x_morko = self.leveys/2
        self.y_morko = 380-self.morko.get_height()
        self.morko_nopeus = 0
        self.morko_laskuri = 0

        # Kolikot
        self.kolikko = pygame.image.load("kolikko.png")
        self.maara = 230 # saa säädettyä kuinka paljon kolikoita sataa. Mitä pienempi, sitä enemmän (min. 2). Suositus 200-300.
        self.kolikot = []
        self.kerattava = 10 # kuinka monta kolikkoa on kerättävä pelin läpäisemiseksi?

        # Tausta
        self.metsa = self.luo_metsa()

        # Kello
        self.kello = pygame.time.Clock()

        # UI
        self.fontti = pygame.font.SysFont("Arial", 24)
        self.fonttiIso = pygame.font.SysFont("Arial", 40)

        # Pelaaminen
        self.nayta_alkutarina()
        self.pisteet = 0
        self.alku_aika = pygame.time.get_ticks()
        self.peliaika = 0
        self.peli_lapi = False
        self.game_over = False
        self.pelisilmukka()
        

    ## Pelaamiseen liittyvät funktiot ##
    ####################################

    def uusi_peli(self):
        # Pelaaja
        self.x = 20
        self.y = 380 - self.robo.get_height()
        self.y_nopeus = 0
        self.maassa = True
        self.oikealle = False
        self.vasemmalle = False

        # Mörkö
        self.x_morko = self.leveys / 2
        self.morko_nopeus = 0
        self.morko_laskuri = 0

        # Kolikot
        self.kolikot.clear()

        # Pisteet ja aika
        self.pisteet = 0
        self.alku_aika = pygame.time.get_ticks()
        self.peliaika = 0

        # Pelitila
        self.peli_lapi = False
        self.game_over = False

        # Uusi metsä (valinnainen jos haluat vaihtuvan maiseman)
        self.metsa = self.luo_metsa()


    def pelisilmukka(self):
        while True:
            for tapahtuma in pygame.event.get():
                self.tutki_tapahtumat(tapahtuma)

            nyt = pygame.time.get_ticks()
            if self.game_over or self.peli_lapi:
                pass
            else:
                self.peliaika = (nyt - self.alku_aika) // 1000

            if self.pisteet >= self.kerattava:
                self.peli_lapi = True

            self.liikuta_roboa()
            self.morko_liikkuu()
            self.kolikon_keraaminen()
            self.osuuko_robotti_morkoon()
            self.piirra_tapahtumat()
            self.kello.tick(60)


    def tutki_tapahtumat(self, tapahtuma):
        if tapahtuma.type == pygame.KEYDOWN:
            if tapahtuma.key == pygame.K_LEFT:
                self.vasemmalle = True
            if tapahtuma.key == pygame.K_RIGHT:
                self.oikealle = True
            if tapahtuma.key == pygame.K_UP and self.maassa:
                self.y_nopeus = -14
                self.maassa = False
            if tapahtuma.key == pygame.K_F2:
                self.uusi_peli()
            if tapahtuma.key == pygame.K_ESCAPE:
                exit()

        if tapahtuma.type == pygame.KEYUP:
            if tapahtuma.key == pygame.K_LEFT:
                self.vasemmalle = False
            if tapahtuma.key == pygame.K_RIGHT:
                self.oikealle = False

        if tapahtuma.type == pygame.QUIT:
            exit()


    def liikuta_roboa(self):
        if not self.peli_lapi:
            if self.oikealle and self.x + self.robo.get_width() <= self.leveys:
                self.x += 3
            if self.vasemmalle and self.x >= 0:
                self.x -= 3
        
        # painovoima hypyssä
        self.y_nopeus += 0.6
        self.y += self.y_nopeus

        #maa
        maa_y = 380 - self.robo.get_height()
        if self.y >= maa_y:
            self.y = maa_y
            self.y_nopeus = 0
            self.maassa = True
    

    def morko_liikkuu(self):
        self.morko_laskuri += 1

        # vaihda suuntaa harvoin
        if self.morko_laskuri > 120:  # noin joka toinen sekunti
            self.morko_nopeus = random.randint(-2, 2) # satunnainen nopeus
            self.morko_laskuri = 0

        self.x_morko += self.morko_nopeus

        # wrap-around (ilmestyy toisesta reunasta)
        if self.x_morko > self.leveys:
            self.x_morko = -self.morko.get_width()

        if self.x_morko < -self.morko.get_width():
            self.x_morko = self.leveys


    def osuuko_robotti_morkoon(self):
        robo_rect = pygame.Rect(self.x, self.y, self.robo.get_width(), self.robo.get_height())
        morko_rect = pygame.Rect(self.x_morko, self.y_morko, self.morko.get_width(), self.morko.get_height())

        if robo_rect.colliderect(morko_rect):
            self.game_over = True


    def luo_kolikot(self):
        return {
            "x": random.randint(0, self.leveys - self.kolikko.get_width()),
            "y": -self.kolikko.get_height(),
            "nopeus": 1
        }


    def kolikon_keraaminen(self):
        robo_rect = pygame.Rect(self.x, self.y, self.robo.get_width(), self.robo.get_height())

        for raha in self.kolikot:
            kolikko_rect = pygame.Rect(raha["x"], raha["y"], self.kolikko.get_width(), self.kolikko.get_height())

            if robo_rect.colliderect(kolikko_rect):
                self.pisteet += 1
                self.kolikot.remove(raha)


    def kolikoita_sataa(self):
        if random.randint(1, self.maara) == 1:
            self.kolikot.append(self.luo_kolikot())

        for raha in self.kolikot:
            raha["y"] += raha["nopeus"]
            raha["x"] += 0

            if raha["y"] >= 380:
                self.pisteet -= 1
                self.kolikot.remove(raha)

            self.naytto.blit(self.kolikko, (raha["x"], raha["y"]))


    ## Pelimaailman piirtämiseen liittyvät funktiot ##
    ##################################################

    def luo_suuri_pilvi(self):
        surf = pygame.Surface((220, 120), pygame.SRCALPHA)
        vari = (255, 255, 255)

        pygame.draw.ellipse(surf, vari, (50, 20, 100, 60))
        pygame.draw.circle(surf, vari, (70, 65), 15)
        pygame.draw.circle(surf, vari, (80, 30), 20)
        pygame.draw.circle(surf, vari, (100, 70), 25)
        pygame.draw.circle(surf, vari, (120, 28), 25)
        pygame.draw.circle(surf, vari, (145, 45), 20)
        pygame.draw.circle(surf, vari, (52, 43), 22)
        pygame.draw.circle(surf, vari, (130, 70), 10)
        pygame.draw.circle(surf, vari, (162, 40), 10)

        return surf


    def luo_pieni_pilvi(self):
        surf = pygame.Surface((220, 120), pygame.SRCALPHA)
        vari = (255, 255, 255)

        pygame.draw.circle(surf, vari, (138, 20), 8)
        pygame.draw.circle(surf, vari, (120, 15), 13)
        pygame.draw.circle(surf, vari, (100, 20), 16)
        pygame.draw.circle(surf, vari, (125, 35), 18)

        return surf


    def piirra_pilvitaivas(self):
        pilvi = self.luo_suuri_pilvi()
        pilvi2 = pygame.transform.flip(pilvi, True, True)
        pilvi3 = pygame.transform.flip(pilvi, True, False)
        pikkupilvi = self.luo_pieni_pilvi()
        pikkupilvi2 = pygame.transform.flip(pikkupilvi, True, True)
        pikkupilvi3 = pygame.transform.flip(pikkupilvi, True, False)
        
        self.naytto.blit(pilvi, (50, 40))
        self.naytto.blit(pilvi, (870, 60))
        self.naytto.blit(pilvi3, (200, 170))
        self.naytto.blit(pilvi2, (600, 100))
        self.naytto.blit(pikkupilvi, (300, 60))
        self.naytto.blit(pikkupilvi2, (450, 120))
        self.naytto.blit(pikkupilvi2, (1100, 150))
        self.naytto.blit(pikkupilvi3, (600, 40))
        self.naytto.blit(pikkupilvi, (800, 200))
        self.naytto.blit(pilvi, (-100, 200))
        self.naytto.blit(pilvi, (1200, 50))
        self.naytto.blit(pilvi, (400, -50))
        self.naytto.blit(pilvi2, (1000, -70))
        self.naytto.blit(pikkupilvi3, (50, 240))


    def piirra_kuusi(self, x, leveys, korkeus):
        pisteet = [
            (x, 350),                 # vasen alakulma
            (x + leveys, 350),        # oikea alakulma
            (x + leveys // 2, 350 - korkeus)  # huippu
        ]
        pygame.draw.polygon(self.naytto, (63, 80, 15), pisteet)


    def luo_metsa(self):
        metsa = []
        x = -10
        while x < self.leveys:
            leveys = random.randint(40, 60)
            korkeus = random.randint(50, 80)

            metsa.append((x, leveys, korkeus))
            x += leveys // 2
        return metsa


    def piirra_metsa(self):
        for x, leveys, korkeus in self.metsa:
            self.piirra_kuusi(x, leveys, korkeus)


    def piirra_tausta(self):
        self.naytto.fill((127, 209, 232)) ## Sininen taivas
        pygame.draw.rect(self.naytto, (132, 164, 39), (0, 350, self.leveys, 130)) # Vihreä maa
        pygame.draw.rect(self.naytto, (188, 165, 131), (0, 370, self.leveys, 30)) # Ruskea tie
        pygame.draw.rect(self.naytto, (104, 75, 43), (0, 430, self.leveys, 60)) # Alareuna
        self.piirra_pilvitaivas() ## Pilvet taivaalle
        self.piirra_metsa() ## Kuusimetsä


    ## UI funktiot ##
    #################

    def keskita_teksti(self, teksti: str, fontti: pygame.font.Font, vari: tuple, y: int):
        teksti = fontti.render(teksti, True, vari)
        teksti_x = self.leveys / 2 - teksti.get_rect().centerx

        self.naytto.blit(teksti, (teksti_x, y))


    def peliohjeet(self):
        teksti = self.fontti.render("Liiku nuolinäppäimillä ← →", True, (255, 255, 255))
        self.naytto.blit(teksti, (20,  440))
        
        teksti = self.fontti.render("Hyppää ↑", True, (255, 255, 255))
        self.naytto.blit(teksti, (300,  440))

        teksti = self.fontti.render("F2 = uusi peli", True, (255, 255, 255))
        self.naytto.blit(teksti, (970, 440))

        teksti = self.fontti.render("Esc = sulje peli", True, (255, 255, 255))
        self.naytto.blit(teksti, (1120,  440))

    def nayta_alkutarina(self):
        alku = pygame.time.get_ticks()
        kesto = 4000  # 4 sekuntia

        while pygame.time.get_ticks() - alku < kesto:
            for tapahtuma in pygame.event.get():
                if tapahtuma.type == pygame.QUIT:
                    exit()

            self.naytto.fill((63, 80, 15))

            self.keskita_teksti("Robitti ja Mörkö", self.fonttiIso, (255, 255, 255), 150)
            self.keskita_teksti("Robitti on robomaailman Robin Hood", self.fontti, (200, 200, 200), 220)
            self.keskita_teksti("Kerää kolikot köyhille, ennenkuin Mörkö saa sinut kiinni.", self.fontti, (200, 200, 200), 260)
            self.keskita_teksti("Tarvittava kolikkomäärä: " + str(self.kerattava), self.fontti, (200, 200, 200), 340)


            pygame.display.flip()
            self.kello.tick(60)


    ## Näytön piirtäminen ##
    ########################

    def piirra_tapahtumat(self):
        self.piirra_tausta()
        self.peliohjeet()
        
        if not self.game_over:
            self.kolikoita_sataa()
            self.naytto.blit(self.robo, (self.x, self.y))
            self.naytto.blit(self.morko, (self.x_morko, self.y_morko))
        else:
            self.keskita_teksti("VOI HARMI!", self.fonttiIso, (202, 83, 75), 120)
            self.keskita_teksti("Mörkö sai sinut kiinni", self.fontti, (202, 83, 75), 200)
            self.keskita_teksti("ja menetit kaikki kolikot!", self.fontti, (202, 83, 75), 230)

        if self.peli_lapi:
            self.keskita_teksti("ONNEA!", self.fonttiIso, (63, 80, 15), 150)
            self.keskita_teksti("Sait kerättyä riittävästi kolikoita!", self.fontti, (63, 80, 15), 200)
            self.maassa = False
            self.morko_nopeus = 0
            self.morko_laskuri = 0
            self.kolikot.clear()

        # Peliaika
        minuutit = self.peliaika // 60
        sekunnit = self.peliaika % 60

        tekstiAika = self.fontti.render(
            f"Aika: {minuutit:02}:{sekunnit:02}",
            True,
            (63, 80, 15)
        )
        self.naytto.blit(tekstiAika, (1100, 50))
        tekstiPisteet = self.fontti.render("Pisteet: " + str(self.pisteet), True, ((63, 80, 15)))
        self.naytto.blit(tekstiPisteet, (1100, 20))
        
        pygame.display.flip()


if __name__ == "__main__":
    Robitti()
    