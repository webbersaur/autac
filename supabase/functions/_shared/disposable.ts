export const DISPOSABLE_DOMAINS: ReadonlySet<string> = new Set([
  "mailinator.com","tempmail.com","guerrillamail.com","throwaway.email","yopmail.com",
  "tempinbox.com","dispostable.com","mailnesia.com","maildrop.cc","fakeinbox.com",
  "sharklasers.com","guerrillamailblock.com","grr.la","guerrillamail.info","guerrillamail.net",
  "guerrillamail.org","guerrillamail.de","trash-mail.com","trashmail.com","trashmail.me",
  "trashmail.net","trashmail.org","trashymail.com","trashymail.net","getnada.com",
  "mailcatch.com","mailexpire.com","mailforspam.com","mailhazard.com","mailhazard.us",
  "mailmoat.com","mailnull.com","mailscrap.com","mailshell.com","mailsiphon.com",
  "mailslite.com","mailzilla.com","mintemail.com","mytemp.email","nomail.xl.cx",
  "nowmymail.com","spamgourmet.com","spamhereplease.com","tempr.email","throwam.com",
  "tmail.ws","tmpmail.net","tmpmail.org","uggsrock.com","veryrealemail.com",
  "wegwerfmail.de","wegwerfmail.net","wh4f.org","whyspam.me","willhackforfood.biz",
  "wooltools.com","wuzup.net","wuzupmail.net","zoemail.org","10minutemail.com",
  "binkmail.com","bobmail.info","chammy.info","devnullmail.com","emailigo.de",
  "emailsensei.com","emailtemporario.com.br","emailwarden.com","fakedemail.com",
  "fastacura.com","filzmail.com","inboxalias.com","jetable.org","klassmaster.com",
  "mailblocks.com","mailinator.net","mailinator2.com","mailmetrash.com","mailnator.com",
  "mytrashmail.com","nobulk.com","noclickemail.com","nogmailspam.info","nomail.pw",
  "nomail2me.com","nospam.ze.tc","nospamfor.us","nowmymail.net","oneoffemail.com",
  "pookmail.com","recode.me","safe-mail.net","safetymail.info","spambox.us",
  "spamcannon.com","spamcannon.net","spamcero.com","spamcon.org","spamcowboy.com",
  "spamcowboy.net","spamcowboy.org","spamday.com","spamex.com","spamfighter.cf",
  "spamfree24.com","spamfree24.de","spamfree24.eu","spamfree24.info","spamfree24.net",
  "spamfree24.org","spamgoes.in","spaml.com","spammotel.com","spamobox.com",
  "spamslicer.com","spamspot.com","spamthis.co.uk","spamtrail.com","tempemail.co.za",
  "tempemail.net","tempmaildemo.com","tempmailer.com","tempomail.fr","temporaryemail.net",
  "temporaryforwarding.com","temporaryinbox.com","temporarymailaddress.com",
  "thankyou2010.com","thisisnotmyrealemail.com","throwawayemailaddress.com",
  "tittbit.in","tradermail.info","turual.com","twinmail.de","veryday.ch",
  "wimsg.com","zetmail.com","zippymail.info","discard.email",
  "mohmal.com","burnermail.io","temp-mail.org","tempail.com","emailondeck.com",
  "crazymailing.com","emkei.cz","mailsac.com","harakirimail.com","33mail.com",
  "maildax.com","tempsky.com","inboxbear.com","anonbox.net","nada.email",
  "tempinbox.co.uk","getairmail.com","bund.us","boximail.com",
  "tempmailaddress.com","spamwc.de","e4ward.com","incognitomail.org","mailtemp.info",
]);

export function isDisposableEmail(email: string): boolean {
  const at = email.lastIndexOf("@");
  if (at < 0) return false;
  return DISPOSABLE_DOMAINS.has(email.slice(at + 1).toLowerCase().trim());
}
