#!/bin/bash
# Lancement du serveur SMTP factice en arrière-plan
php /usr/local/bin/smtp_server.php &

# Lancement de Apache au premier plan
apache2-foreground
