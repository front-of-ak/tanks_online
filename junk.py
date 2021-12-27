running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # make bullet if you press left mouse button
                angle, x, y = player_tank.get_position_and_angle_for_bullet()
                Bullet(angle, x, y)

    screen.fill(BACKGROUND)

    check_pressed()

    all_sprites.draw(screen)
    all_sprites.update()

    pygame.display.flip()
    clock.tick(FPS)
