import pygame as pg


def debugging(info, font, y = 10, x = 10):
    display_surface = pg.display.get_surface()
    debug_surf = font.render(info, True, 'White')
    debug_rect = debug_surf.get_rect(topleft = (x,y))
    pg.draw.rect(display_surface,'Black',debug_rect)
    display_surface.blit(debug_surf,debug_rect)
