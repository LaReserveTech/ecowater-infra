import { AlertLevel, MailType } from '../types'

type MailUser = {
  Email: string
  Name: string
}
export type Mail = {
  From: MailUser
  To: MailUser[]
  TemplateID: number
  TemplateLanguage: boolean
  Subject: string
  Variables: {
    mailType: MailType
    niveau?: string
  }
}

const ALERT_LEVEL_TRAD = Object.freeze({
  vigilance: 'de vigilance',
  alerte: "d'alerte",
  'alerte renforcée': "d'alerte renforcée",
  crise: 'de crise',
})

export const createEmail = (emailAddress: string, mailType: MailType, alertLevel: AlertLevel | undefined): Mail => {
  return {
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
    TemplateID: 5454985,
    TemplateLanguage: true,
    Subject:
      mailType === 'decree_repeal'
        ? "Les restrictions de votre territoire viennent d'être levées"
        : "Votre territoire passe en état {{var:niveau:''}}",
    Variables: {
      mailType,
      niveau: alertLevel ? ALERT_LEVEL_TRAD[alertLevel] : undefined,
    },
  }
}
