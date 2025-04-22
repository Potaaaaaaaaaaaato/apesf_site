import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class ComplexPasswordValidator:
    def validate(self, password, user=None):
        # Vérifie la présence d'au moins une majuscule
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Le mot de passe doit contenir au moins une lettre majuscule (sans accent)."),
                code='password_no_upper',
            )
        # Vérifie la présence d'au moins une minuscule
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("Le mot de passe doit contenir au moins une lettre minuscule (sans accent)."),
                code='password_no_lower',
            )
        # Vérifie la présence d'au moins un chiffre
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _("Le mot de passe doit contenir au moins un chiffre."),
                code='password_no_number',
            )
        # Vérifie la présence d'au moins un caractère spécial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("Le mot de passe doit contenir au moins un caractère spécial parmis cette liste : (!@#$%^&*(),.?\":{}|<>)."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Votre mot de passe doit contenir au moins 12 caractères, une majuscule, une minuscule, un chiffre, et un caractère spécial."
        )