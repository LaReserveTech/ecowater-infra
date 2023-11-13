export type Mail = {
  From: {
    Email: string
    Name: string
  }
  To: [
    {
      Email: string
      Name: string
    }
  ]
  TemplateID: number
  TemplateLanguage: boolean
  Subject: string
  Variables: {
    niveau: string
  }
}

export const createEmail = (emailAddress: string): Mail => ({
  From: {
    Email: 'florian@alerte-secheresse.fr',
    Name: 'Alerte Sécheresse',
  },
  To: [
    {
      Email: emailAddress,
      Name: emailAddress,
    },
  ],
  TemplateID: 4732985,
  TemplateLanguage: true,
  Subject: 'renforcée',
  Variables: {
    niveau: 'maximale',
  },
})
