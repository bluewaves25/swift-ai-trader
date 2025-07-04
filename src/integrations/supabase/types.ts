export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  public: {
    Tables: {
      ai_signals: {
        Row: {
          confidence: number
          created_at: string | null
          entry_price: number | null
          executed: boolean | null
          id: string
          pair_id: string | null
          reasoning: string | null
          signal: Database["public"]["Enums"]["signal_type"]
          stop_loss: number | null
          strategy_used: Database["public"]["Enums"]["strategy_type"]
          take_profit: number | null
        }
        Insert: {
          confidence: number
          created_at?: string | null
          entry_price?: number | null
          executed?: boolean | null
          id?: string
          pair_id?: string | null
          reasoning?: string | null
          signal: Database["public"]["Enums"]["signal_type"]
          stop_loss?: number | null
          strategy_used: Database["public"]["Enums"]["strategy_type"]
          take_profit?: number | null
        }
        Update: {
          confidence?: number
          created_at?: string | null
          entry_price?: number | null
          executed?: boolean | null
          id?: string
          pair_id?: string | null
          reasoning?: string | null
          signal?: Database["public"]["Enums"]["signal_type"]
          stop_loss?: number | null
          strategy_used?: Database["public"]["Enums"]["strategy_type"]
          take_profit?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "ai_signals_pair_id_fkey"
            columns: ["pair_id"]
            isOneToOne: false
            referencedRelation: "trading_pairs"
            referencedColumns: ["id"]
          },
        ]
      }
      market_data: {
        Row: {
          bollinger_lower: number | null
          bollinger_upper: number | null
          close_price: number
          high_price: number
          id: string
          low_price: number
          macd: number | null
          market_condition:
            | Database["public"]["Enums"]["market_condition"]
            | null
          open_price: number
          pair_id: string | null
          resistance_level: number | null
          rsi: number | null
          support_level: number | null
          timestamp: string | null
          volatility: number | null
          volume: number
        }
        Insert: {
          bollinger_lower?: number | null
          bollinger_upper?: number | null
          close_price: number
          high_price: number
          id?: string
          low_price: number
          macd?: number | null
          market_condition?:
            | Database["public"]["Enums"]["market_condition"]
            | null
          open_price: number
          pair_id?: string | null
          resistance_level?: number | null
          rsi?: number | null
          support_level?: number | null
          timestamp?: string | null
          volatility?: number | null
          volume: number
        }
        Update: {
          bollinger_lower?: number | null
          bollinger_upper?: number | null
          close_price?: number
          high_price?: number
          id?: string
          low_price?: number
          macd?: number | null
          market_condition?:
            | Database["public"]["Enums"]["market_condition"]
            | null
          open_price?: number
          pair_id?: string | null
          resistance_level?: number | null
          rsi?: number | null
          support_level?: number | null
          timestamp?: string | null
          volatility?: number | null
          volume?: number
        }
        Relationships: [
          {
            foreignKeyName: "market_data_pair_id_fkey"
            columns: ["pair_id"]
            isOneToOne: false
            referencedRelation: "trading_pairs"
            referencedColumns: ["id"]
          },
        ]
      }
      pair_strategies: {
        Row: {
          confidence_score: number | null
          current_strategy: Database["public"]["Enums"]["strategy_type"]
          id: string
          last_updated: string | null
          pair_id: string | null
          performance_score: number | null
          strategy_params: Json | null
          total_trades: number | null
          winning_trades: number | null
        }
        Insert: {
          confidence_score?: number | null
          current_strategy: Database["public"]["Enums"]["strategy_type"]
          id?: string
          last_updated?: string | null
          pair_id?: string | null
          performance_score?: number | null
          strategy_params?: Json | null
          total_trades?: number | null
          winning_trades?: number | null
        }
        Update: {
          confidence_score?: number | null
          current_strategy?: Database["public"]["Enums"]["strategy_type"]
          id?: string
          last_updated?: string | null
          pair_id?: string | null
          performance_score?: number | null
          strategy_params?: Json | null
          total_trades?: number | null
          winning_trades?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "pair_strategies_pair_id_fkey"
            columns: ["pair_id"]
            isOneToOne: true
            referencedRelation: "trading_pairs"
            referencedColumns: ["id"]
          },
        ]
      }
      performance_analytics: {
        Row: {
          avg_profit_per_trade: number | null
          created_at: string | null
          date: string
          id: string
          max_drawdown: number | null
          sharpe_ratio: number | null
          total_profit: number | null
          total_trades: number | null
          total_volume: number | null
          win_rate: number | null
          winning_trades: number | null
        }
        Insert: {
          avg_profit_per_trade?: number | null
          created_at?: string | null
          date: string
          id?: string
          max_drawdown?: number | null
          sharpe_ratio?: number | null
          total_profit?: number | null
          total_trades?: number | null
          total_volume?: number | null
          win_rate?: number | null
          winning_trades?: number | null
        }
        Update: {
          avg_profit_per_trade?: number | null
          created_at?: string | null
          date?: string
          id?: string
          max_drawdown?: number | null
          sharpe_ratio?: number | null
          total_profit?: number | null
          total_trades?: number | null
          total_volume?: number | null
          win_rate?: number | null
          winning_trades?: number | null
        }
        Relationships: []
      }
      portfolios: {
        Row: {
          available_balance: number | null
          created_at: string | null
          id: string
          realized_pnl: number | null
          total_balance: number | null
          total_trades: number | null
          unrealized_pnl: number | null
          updated_at: string | null
          user_id: string | null
          winning_trades: number | null
        }
        Insert: {
          available_balance?: number | null
          created_at?: string | null
          id?: string
          realized_pnl?: number | null
          total_balance?: number | null
          total_trades?: number | null
          unrealized_pnl?: number | null
          updated_at?: string | null
          user_id?: string | null
          winning_trades?: number | null
        }
        Update: {
          available_balance?: number | null
          created_at?: string | null
          id?: string
          realized_pnl?: number | null
          total_balance?: number | null
          total_trades?: number | null
          unrealized_pnl?: number | null
          updated_at?: string | null
          user_id?: string | null
          winning_trades?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "portfolios_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      profiles: {
        Row: {
          address: string | null
          avatar_url: string | null
          bio: string | null
          created_at: string
          date_of_birth: string | null
          full_name: string | null
          id: string
          investment_experience: string | null
          nationality: string | null
          occupation: string | null
          phone: string | null
          updated_at: string
          user_id: string
        }
        Insert: {
          address?: string | null
          avatar_url?: string | null
          bio?: string | null
          created_at?: string
          date_of_birth?: string | null
          full_name?: string | null
          id?: string
          investment_experience?: string | null
          nationality?: string | null
          occupation?: string | null
          phone?: string | null
          updated_at?: string
          user_id: string
        }
        Update: {
          address?: string | null
          avatar_url?: string | null
          bio?: string | null
          created_at?: string
          date_of_birth?: string | null
          full_name?: string | null
          id?: string
          investment_experience?: string | null
          nationality?: string | null
          occupation?: string | null
          phone?: string | null
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      risk_settings: {
        Row: {
          created_at: string | null
          id: string
          max_daily_loss: number | null
          max_open_positions: number | null
          max_position_size: number | null
          risk_per_trade: number | null
          stop_loss_percentage: number | null
          take_profit_percentage: number | null
          user_id: string | null
        }
        Insert: {
          created_at?: string | null
          id?: string
          max_daily_loss?: number | null
          max_open_positions?: number | null
          max_position_size?: number | null
          risk_per_trade?: number | null
          stop_loss_percentage?: number | null
          take_profit_percentage?: number | null
          user_id?: string | null
        }
        Update: {
          created_at?: string | null
          id?: string
          max_daily_loss?: number | null
          max_open_positions?: number | null
          max_position_size?: number | null
          risk_per_trade?: number | null
          stop_loss_percentage?: number | null
          take_profit_percentage?: number | null
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "risk_settings_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: true
            referencedRelation: "users"
            referencedColumns: ["id"]
          },
        ]
      }
      support_tickets: {
        Row: {
          created_at: string
          id: string
          message: string
          priority: string
          status: string
          subject: string
          updated_at: string
          user_id: string
        }
        Insert: {
          created_at?: string
          id?: string
          message: string
          priority?: string
          status?: string
          subject: string
          updated_at?: string
          user_id: string
        }
        Update: {
          created_at?: string
          id?: string
          message?: string
          priority?: string
          status?: string
          subject?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      trades: {
        Row: {
          amount: number
          closed_at: string | null
          created_at: string | null
          entry_price: number
          execution_time: string | null
          exit_price: number | null
          id: string
          pair_id: string | null
          profit_loss: number | null
          signal_id: string | null
          status: Database["public"]["Enums"]["trade_status"] | null
          stop_loss: number | null
          take_profit: number | null
          trade_type: Database["public"]["Enums"]["trade_type"]
        }
        Insert: {
          amount: number
          closed_at?: string | null
          created_at?: string | null
          entry_price: number
          execution_time?: string | null
          exit_price?: number | null
          id?: string
          pair_id?: string | null
          profit_loss?: number | null
          signal_id?: string | null
          status?: Database["public"]["Enums"]["trade_status"] | null
          stop_loss?: number | null
          take_profit?: number | null
          trade_type: Database["public"]["Enums"]["trade_type"]
        }
        Update: {
          amount?: number
          closed_at?: string | null
          created_at?: string | null
          entry_price?: number
          execution_time?: string | null
          exit_price?: number | null
          id?: string
          pair_id?: string | null
          profit_loss?: number | null
          signal_id?: string | null
          status?: Database["public"]["Enums"]["trade_status"] | null
          stop_loss?: number | null
          take_profit?: number | null
          trade_type?: Database["public"]["Enums"]["trade_type"]
        }
        Relationships: [
          {
            foreignKeyName: "trades_pair_id_fkey"
            columns: ["pair_id"]
            isOneToOne: false
            referencedRelation: "trading_pairs"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "trades_signal_id_fkey"
            columns: ["signal_id"]
            isOneToOne: false
            referencedRelation: "ai_signals"
            referencedColumns: ["id"]
          },
        ]
      }
      trading_pairs: {
        Row: {
          base_currency: string
          created_at: string | null
          id: string
          is_active: boolean | null
          max_trade_amount: number | null
          min_trade_amount: number | null
          quote_currency: string
          symbol: string
        }
        Insert: {
          base_currency: string
          created_at?: string | null
          id?: string
          is_active?: boolean | null
          max_trade_amount?: number | null
          min_trade_amount?: number | null
          quote_currency: string
          symbol: string
        }
        Update: {
          base_currency?: string
          created_at?: string | null
          id?: string
          is_active?: boolean | null
          max_trade_amount?: number | null
          min_trade_amount?: number | null
          quote_currency?: string
          symbol?: string
        }
        Relationships: []
      }
      transactions: {
        Row: {
          amount: number
          created_at: string
          exness_account: string | null
          id: string
          notes: string | null
          reference_id: string | null
          status: string
          type: string
          updated_at: string
          user_id: string
        }
        Insert: {
          amount: number
          created_at?: string
          exness_account?: string | null
          id?: string
          notes?: string | null
          reference_id?: string | null
          status?: string
          type: string
          updated_at?: string
          user_id: string
        }
        Update: {
          amount?: number
          created_at?: string
          exness_account?: string | null
          id?: string
          notes?: string | null
          reference_id?: string | null
          status?: string
          type?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      user_settings: {
        Row: {
          created_at: string
          dark_mode: boolean | null
          email_notifications: boolean | null
          id: string
          language: string | null
          sms_notifications: boolean | null
          timezone: string | null
          trade_alerts: boolean | null
          updated_at: string
          user_id: string
        }
        Insert: {
          created_at?: string
          dark_mode?: boolean | null
          email_notifications?: boolean | null
          id?: string
          language?: string | null
          sms_notifications?: boolean | null
          timezone?: string | null
          trade_alerts?: boolean | null
          updated_at?: string
          user_id: string
        }
        Update: {
          created_at?: string
          dark_mode?: boolean | null
          email_notifications?: boolean | null
          id?: string
          language?: string | null
          sms_notifications?: boolean | null
          timezone?: string | null
          trade_alerts?: boolean | null
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      users: {
        Row: {
          created_at: string | null
          email: string
          id: string
          role: Database["public"]["Enums"]["user_role"]
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          email: string
          id?: string
          role?: Database["public"]["Enums"]["user_role"]
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          email?: string
          id?: string
          role?: Database["public"]["Enums"]["user_role"]
          updated_at?: string | null
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      market_condition: "trending_up" | "trending_down" | "ranging" | "volatile"
      signal_type: "buy" | "sell" | "hold"
      strategy_type:
        | "breakout"
        | "mean_reversion"
        | "momentum"
        | "scalping"
        | "grid"
      trade_status: "pending" | "executed" | "cancelled" | "failed"
      trade_type: "buy" | "sell"
      user_role: "owner" | "investor"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DefaultSchema = Database[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof (Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        Database[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? (Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      Database[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof Database },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends { schema: keyof Database }
  ? Database[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof Database },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends { schema: keyof Database }
  ? Database[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {
      market_condition: ["trending_up", "trending_down", "ranging", "volatile"],
      signal_type: ["buy", "sell", "hold"],
      strategy_type: [
        "breakout",
        "mean_reversion",
        "momentum",
        "scalping",
        "grid",
      ],
      trade_status: ["pending", "executed", "cancelled", "failed"],
      trade_type: ["buy", "sell"],
      user_role: ["owner", "investor"],
    },
  },
} as const
