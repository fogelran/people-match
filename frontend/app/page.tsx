"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

type Question = {
  id: number;
  text: string;
};

type Match = {
  match: string | null;
  score: number | null;
};

export default function HomePage() {
  const [activeUser, setActiveUser] = useState<string | null>(null);
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [registerUsername, setRegisterUsername] = useState("");
  const [registerPassword, setRegisterPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [question, setQuestion] = useState<Question | null>(null);
  const [match, setMatch] = useState<Match>({ match: null, score: null });
  const [askQuestionText, setAskQuestionText] = useState("");
  const [askDesiredAnswer, setAskDesiredAnswer] = useState("yes");
  const [addDesiredAnswer, setAddDesiredAnswer] = useState("yes");
  const [loading, setLoading] = useState(false);

  const isAuthenticated = useMemo(() => Boolean(activeUser), [activeUser]);

  const loadStoredUser = useCallback(() => {
    if (typeof window === "undefined") {
      return;
    }
    const stored = window.localStorage.getItem("people-match-user");
    if (stored) {
      setActiveUser(stored);
    }
  }, []);

  const persistUser = (username: string) => {
    setActiveUser(username);
    if (typeof window !== "undefined") {
      window.localStorage.setItem("people-match-user", username);
    }
  };

  const clearUser = () => {
    setActiveUser(null);
    setQuestion(null);
    setMatch({ match: null, score: null });
    if (typeof window !== "undefined") {
      window.localStorage.removeItem("people-match-user");
    }
  };

  const fetchNextQuestion = useCallback(
    async (username: string) => {
      const response = await fetch(
        `${API_BASE}/api/questions/next?username=${encodeURIComponent(username)}`
      );
      if (!response.ok) {
        return;
      }
      const data = await response.json();
      setQuestion(data.question ?? null);
    },
    []
  );

  const fetchMatch = useCallback(async (username: string) => {
    const response = await fetch(
      `${API_BASE}/api/match/check?username=${encodeURIComponent(username)}`
    );
    if (!response.ok) {
      return;
    }
    const data = (await response.json()) as Match;
    setMatch({ match: data.match, score: data.score });
  }, []);

  const handleLogin = async () => {
    setError(null);
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: loginUsername.trim(), password: loginPassword })
      });
      if (!response.ok) {
        throw new Error("Login failed");
      }
      persistUser(loginUsername.trim());
      await fetchNextQuestion(loginUsername.trim());
      await fetchMatch(loginUsername.trim());
    } catch (err) {
      setError("We couldn't sign you in. Double-check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async () => {
    setError(null);
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: registerUsername.trim(),
          password: registerPassword
        })
      });
      if (!response.ok) {
        throw new Error("Registration failed");
      }
      persistUser(registerUsername.trim());
      await fetchNextQuestion(registerUsername.trim());
      await fetchMatch(registerUsername.trim());
    } catch (err) {
      setError("We couldn't create your account. Try a new username.");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = async (answer: boolean) => {
    if (!activeUser || !question) {
      return;
    }
    await fetch(`${API_BASE}/api/questions/answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: activeUser,
        question_id: question.id,
        answer
      })
    });
    await fetchNextQuestion(activeUser);
    await fetchMatch(activeUser);
  };

  const handleSkip = async () => {
    if (!activeUser || !question) {
      return;
    }
    await fetch(`${API_BASE}/api/questions/skip`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: activeUser,
        question_id: question.id
      })
    });
    await fetchNextQuestion(activeUser);
  };

  const handleAddExisting = async () => {
    if (!activeUser || !question) {
      return;
    }
    await fetch(`${API_BASE}/api/questions/ask-existing`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: activeUser,
        question_id: question.id,
        desired_answer: addDesiredAnswer === "yes"
      })
    });
    await fetchMatch(activeUser);
  };

  const handleAskQuestion = async () => {
    if (!activeUser || !askQuestionText.trim()) {
      return;
    }
    await fetch(`${API_BASE}/api/questions/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: activeUser,
        question_text: askQuestionText.trim(),
        desired_answer: askDesiredAnswer === "yes"
      })
    });
    setAskQuestionText("");
    await fetchMatch(activeUser);
  };

  useEffect(() => {
    loadStoredUser();
  }, [loadStoredUser]);

  useEffect(() => {
    if (!activeUser) {
      return;
    }
    fetchNextQuestion(activeUser);
    fetchMatch(activeUser);
  }, [activeUser, fetchNextQuestion, fetchMatch]);

  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-4xl space-y-6">
        <header className="flex flex-col gap-2 text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-slate-400">
            People Match
          </p>
          <h1 className="text-3xl font-semibold text-slate-900">
            Build mutual connections through shared answers.
          </h1>
        </header>

        {!isAuthenticated ? (
          <Card className="mx-auto max-w-xl">
            <CardHeader>
              <CardTitle>Welcome back</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Tabs defaultValue="login">
                <TabsList className="grid grid-cols-2">
                  <TabsTrigger value="login">Login</TabsTrigger>
                  <TabsTrigger value="register">Register</TabsTrigger>
                </TabsList>
                <TabsContent value="login">
                  <div className="space-y-3">
                    <div>
                      <Label htmlFor="login-username">Username</Label>
                      <Input
                        id="login-username"
                        value={loginUsername}
                        onChange={(event) => setLoginUsername(event.target.value)}
                        placeholder="you@example.com"
                      />
                    </div>
                    <div>
                      <Label htmlFor="login-password">Password</Label>
                      <Input
                        id="login-password"
                        type="password"
                        value={loginPassword}
                        onChange={(event) => setLoginPassword(event.target.value)}
                        placeholder="••••••••"
                      />
                    </div>
                    <Button className="w-full" onClick={handleLogin} disabled={loading}>
                      Sign in
                    </Button>
                  </div>
                </TabsContent>
                <TabsContent value="register">
                  <div className="space-y-3">
                    <div>
                      <Label htmlFor="register-username">Username</Label>
                      <Input
                        id="register-username"
                        value={registerUsername}
                        onChange={(event) => setRegisterUsername(event.target.value)}
                        placeholder="choose a username"
                      />
                    </div>
                    <div>
                      <Label htmlFor="register-password">Password</Label>
                      <Input
                        id="register-password"
                        type="password"
                        value={registerPassword}
                        onChange={(event) => setRegisterPassword(event.target.value)}
                        placeholder="Create a secure password"
                      />
                    </div>
                    <Button className="w-full" onClick={handleRegister} disabled={loading}>
                      Create account
                    </Button>
                  </div>
                </TabsContent>
              </Tabs>
              {error ? <p className="text-sm text-red-500">{error}</p> : null}
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
            <Card>
              <CardHeader className="space-y-2">
                <CardTitle className="flex items-center justify-between">
                  <span>Daily question</span>
                  <Button variant="ghost" onClick={clearUser}>
                    Log out
                  </Button>
                </CardTitle>
                <p className="text-sm text-slate-500">
                  Answer one question at a time. Add it to your asked list if it matters to you.
                </p>
              </CardHeader>
              <CardContent className="space-y-4">
                {question ? (
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                    <p className="text-lg font-semibold text-slate-900">{question.text}</p>
                  </div>
                ) : (
                  <div className="rounded-lg border border-dashed border-slate-300 p-4 text-sm text-slate-500">
                    You are all caught up. Check back soon for more questions.
                  </div>
                )}
                <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                  <Button onClick={() => handleAnswer(true)} disabled={!question}>
                    Yes
                  </Button>
                  <Button variant="secondary" onClick={() => handleAnswer(false)} disabled={!question}>
                    No
                  </Button>
                  <Button variant="ghost" onClick={handleSkip} disabled={!question}>
                    Skip
                  </Button>
                  <Button variant="secondary" onClick={handleAddExisting} disabled={!question}>
                    Add to my asked list
                  </Button>
                </div>
                <div className="space-y-1">
                  <Label>Desired answer when you ask it</Label>
                  <Select value={addDesiredAnswer} onValueChange={setAddDesiredAnswer}>
                    <SelectTrigger>
                      <SelectValue placeholder="Desired answer" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="yes">Yes</SelectItem>
                      <SelectItem value="no">No</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Ask your question</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-1">
                    <Label htmlFor="ask-question">Your question</Label>
                    <Input
                      id="ask-question"
                      value={askQuestionText}
                      onChange={(event) => setAskQuestionText(event.target.value)}
                      placeholder="e.g., Do you love weekend road trips?"
                    />
                  </div>
                  <div className="space-y-1">
                    <Label>Desired answer</Label>
                    <Select value={askDesiredAnswer} onValueChange={setAskDesiredAnswer}>
                      <SelectTrigger>
                        <SelectValue placeholder="Desired answer" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="yes">Yes</SelectItem>
                        <SelectItem value="no">No</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button onClick={handleAskQuestion} disabled={!askQuestionText.trim()}>
                    Add question
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Potential match</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {match.match ? (
                    <div className="space-y-1">
                      <p className="text-lg font-semibold text-slate-900">{match.match}</p>
                      <p className="text-sm text-slate-500">
                        Mutual answers align with your desired outcomes.
                      </p>
                    </div>
                  ) : (
                    <p className="text-sm text-slate-500">
                      Keep answering questions to discover a mutual match.
                    </p>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
