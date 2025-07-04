
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY')

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface SupportTicket {
  userEmail: string;
  subject: string;
  message: string;
  priority: string;
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders })
  }

  try {
    const { userEmail, subject, message, priority }: SupportTicket = await req.json()

    if (!RESEND_API_KEY) {
      console.error('RESEND_API_KEY is not set')
      return new Response(
        JSON.stringify({ error: 'Email service not configured' }),
        { 
          status: 500, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        }
      )
    }

    const emailData = {
      from: 'support@wavesquant.com',
      to: ['adus7661@gmail.com'], // Your email for support notifications
      subject: `[${priority.toUpperCase()}] Support Ticket: ${subject}`,
      html: `
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #333; border-bottom: 2px solid #6366f1; padding-bottom: 10px;">New Support Ticket</h2>
          
          <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin: 0 0 15px 0; color: #495057;">Ticket Details</h3>
            <div style="margin-bottom: 10px;"><strong>From:</strong> ${userEmail}</div>
            <div style="margin-bottom: 10px;"><strong>Priority:</strong> 
              <span style="color: ${priority === 'urgent' ? '#dc3545' : priority === 'high' ? '#fd7e14' : '#28a745'}; font-weight: bold;">
                ${priority.toUpperCase()}
              </span>
            </div>
            <div style="margin-bottom: 10px;"><strong>Subject:</strong> ${subject}</div>
            <div><strong>Submitted:</strong> ${new Date().toLocaleString()}</div>
          </div>
          
          <div style="background: #fff; border: 1px solid #dee2e6; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h4 style="margin: 0 0 15px 0; color: #495057;">Message:</h4>
            <div style="line-height: 1.6; color: #6c757d; white-space: pre-wrap;">${message}</div>
          </div>
          
          <div style="margin-top: 20px; padding: 15px; background: #e9ecef; border-radius: 8px; border-left: 4px solid #6366f1;">
            <p style="margin: 0; font-size: 14px; color: #6c757d;">
              <strong>Action Required:</strong> Please respond to the user at: <a href="mailto:${userEmail}" style="color: #6366f1;">${userEmail}</a>
            </p>
            <p style="margin: 8px 0 0 0; font-size: 12px; color: #868e96;">
              This ticket was submitted through the Waves Quant Engine support system.
            </p>
          </div>
        </div>
      `
    }

    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(emailData),
    })

    if (!response.ok) {
      const error = await response.text()
      console.error('Failed to send email:', error)
      throw new Error('Failed to send support notification email')
    }

    const result = await response.json()
    console.log('Support notification email sent successfully:', result)

    return new Response(
      JSON.stringify({ success: true, id: result.id }),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )

  } catch (error) {
    console.error('Error in support-notify function:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )
  }
})
