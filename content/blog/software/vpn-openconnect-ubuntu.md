---
Title: VPN with openconnect in Ubuntu 14.10
Date: 2015-05-12
Category: Software
Status: published
---

Many services that my university offers have one requirement: to be in a trusted network. That is either eduroam or any network where you can connect through a VPN tunnel. As sad as it is, I don't have an eduroam router next to my home. However, I ran into some minor problems when trying to create a VPN connection with network-manager.

## The Good

After installing the necessary dependencies `network-manager-openconnect` and `network-manager-openconnect-gnome` there was a rather visual problem: When trying to create a VPN connection, network-manager would just present me with the option to *Import from File...*. Not a glimpse of my beloved *Cisco AnyConnect Compatible VPN (openconnect)* option. So what do?

The fix is very easy. There seems to be a minor rights issue where only superusers can create openconnect VPNs. So simply fire up a shell and enter

```sh
gksudo nm-connection-editor
```

After entering your sudo password you'll be rewarded with a dialog listing all your network connections. Press **Add** to the right and there you'll find the option for an openconnect VPN connection. Enter your credentials and link the CA cert. Don't forget to enable *All users may connect to this network* in the "General" tab. That way you'll be able to use the connection as a non-superuser.

If you're from the TU Dresden, use the following data:

**Gateway:** vpn2.zih.tu-dresden.de
**CA Certificate:** Download [here](https://pki.pca.dfn.de/tu-dresden-ca/pub/cacert/chain.txt) (*Right click - Save link as<* tud-cacert.pem)

Leave the rest as it is and connect through your network manager as usual. Enter your ZIH login and password and you're in! Speaking of, the ZIH also has [a page on openconnect](https://tu-dresden.de/die_tu_dresden/zentrale_einrichtungen/zih/dienste/datennetz_dienste/vpn/). But it's only available in German and doesn't consider the above problem with network-manager in Ubuntu 14.10.

## The Bad

*Why not use OpenVPN?* - Well, Cisco AnyConnect servers are not OpenVPN servers. Incompatible.
*What about vpnc?* - Also incompatible. That's something different. Either openconnect or ...

## The Ugly

Cisco AnyConnect! I mean, the TU recommends it so what could possibly go wrong? There is even a Linux version!

After the (refreshingly easy) installation I continue to start up the UI with

```sh
./anyconnect-3.1.05182/vpn/vpnui
```
and when you try to login you're greeted with the error message

![Dafuq, Cisco?]({static}/images/anyconnect-error.png)

*"A VPN CONNECTION CANNOT BE WHAT??"* - I google'd, duckduckgo'd and even bing'd but there were no solutions in sight. I got fed up and decided that the crappy Linux port is not worth debugging. That's how I ended up with openconnect. To this date I cannot offer any solution to the notorious *file move error* of the Cisco AnyConnect Secure Mobility Client. I can just tell everyone reading this that openconnect is the alternative you should consider.
