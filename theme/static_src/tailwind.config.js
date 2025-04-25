module.exports = {
    content: [
      '../templates/**/*.html',
      '../../templates/**/*.html',
      '../../**/templates/**/*.html',
    ],
    theme: {
      extend: {
        colors: {
          primary: {
            500: '#015489', // Bleu doux pour les boutons et liens
            600: '#3B82F6',
          },
          secondary: {
            500: '#FDBA74', // Orange chaleureux pour les accents
            600: '#FB923C',
          },
          neutral: {
            50: '#FFF7ED', // Blanc cassé pour les fonds
            100: '#F3F4F6', // Gris clair pour le footer
            600: '#4B5563', // Gris foncé pour le texte
          },
        },
        fontFamily: {
          poppins: ['Poppins', 'sans-serif'], // Police Poppins
        },
      },
    },
    plugins: [],
  }