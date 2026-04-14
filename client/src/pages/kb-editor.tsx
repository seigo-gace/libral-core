import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { queryClient, apiRequest } from "@/lib/queryClient";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Search, Plus, Edit2, Trash2, Save, X } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface KBEntry {
  id: string;
  content: string;
  language: string;
  category: string;
  metadata: {
    source: string;
    confidence: number;
    created_at: string;
    updated_at: string;
  };
}

export default function KBEditor() {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState("");
  const [editingEntry, setEditingEntry] = useState<KBEntry | null>(null);
  const [newEntry, setNewEntry] = useState({ content: "", language: "en", category: "" });
  const [showNewForm, setShowNewForm] = useState(false);

  // Fetch KB entries
  const { data: entriesData, isLoading } = useQuery({
    queryKey: ["/api/kb/entries"],
  });

  const entries = entriesData?.entries || [];

  // Create entry mutation
  const createMutation = useMutation({
    mutationFn: async (entry: { content: string; language: string; category: string }) => {
      return apiRequest("/api/kb/entries", "POST", entry);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/kb/entries"] });
      setNewEntry({ content: "", language: "en", category: "" });
      setShowNewForm(false);
      toast({ title: "KB Entry Created", description: "Knowledge base entry added successfully" });
    },
  });

  // Update entry mutation
  const updateMutation = useMutation({
    mutationFn: async (entry: KBEntry) => {
      return apiRequest(`/api/kb/entries/${entry.id}`, "PUT", {
        content: entry.content,
        language: entry.language,
        category: entry.category,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/kb/entries"] });
      setEditingEntry(null);
      toast({ title: "KB Entry Updated", description: "Knowledge base entry updated successfully" });
    },
  });

  // Delete entry mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      return apiRequest(`/api/kb/entries/${id}`, "DELETE");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/kb/entries"] });
      toast({ title: "KB Entry Deleted", description: "Knowledge base entry deleted successfully" });
    },
  });

  const filteredEntries = entries.filter((entry: KBEntry) =>
    entry.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
    entry.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-black text-cyan-400 font-mono p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2 neon-text">📚 KB EDITOR</h1>
          <p className="text-cyan-500">Knowledge Base Management System</p>
        </div>

        {/* Search & Actions */}
        <div className="mb-6 flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-cyan-500" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search KB entries..."
              className="pl-10 bg-black border-cyan-500 text-cyan-400"
              data-testid="input-kb-search"
            />
          </div>
          <Button
            onClick={() => setShowNewForm(true)}
            className="bg-cyan-500 hover:bg-cyan-600 text-black"
            data-testid="button-add-kb-entry"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Entry
          </Button>
        </div>

        {/* New Entry Form */}
        {showNewForm && (
          <Card className="mb-6 border-cyan-500 bg-black/50">
            <CardHeader>
              <CardTitle className="text-cyan-400">New KB Entry</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                value={newEntry.content}
                onChange={(e) => setNewEntry({ ...newEntry, content: e.target.value })}
                placeholder="Enter knowledge content..."
                className="bg-black border-cyan-500 text-cyan-400"
                rows={4}
                data-testid="textarea-kb-content"
              />
              <div className="flex gap-4">
                <Select
                  value={newEntry.language}
                  onValueChange={(value) => setNewEntry({ ...newEntry, language: value })}
                >
                  <SelectTrigger className="bg-black border-cyan-500 text-cyan-400" data-testid="select-kb-language">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="ja">Japanese</SelectItem>
                    <SelectItem value="zh">Chinese</SelectItem>
                    <SelectItem value="es">Spanish</SelectItem>
                  </SelectContent>
                </Select>
                <Input
                  value={newEntry.category}
                  onChange={(e) => setNewEntry({ ...newEntry, category: e.target.value })}
                  placeholder="Category (e.g., technical, business)"
                  className="bg-black border-cyan-500 text-cyan-400"
                  data-testid="input-kb-category"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  onClick={() => createMutation.mutate(newEntry)}
                  disabled={!newEntry.content || !newEntry.category || createMutation.isPending}
                  className="bg-cyan-500 hover:bg-cyan-600 text-black"
                  data-testid="button-save-kb-entry"
                >
                  <Save className="w-4 h-4 mr-2" />
                  Save
                </Button>
                <Button
                  onClick={() => setShowNewForm(false)}
                  variant="outline"
                  className="border-cyan-500 text-cyan-400"
                  data-testid="button-cancel-kb-entry"
                >
                  <X className="w-4 h-4 mr-2" />
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* KB Entries List */}
        <div className="space-y-4">
          {isLoading ? (
            <p className="text-cyan-500">Loading KB entries...</p>
          ) : filteredEntries.length === 0 ? (
            <p className="text-cyan-500">No KB entries found</p>
          ) : (
            filteredEntries.map((entry: KBEntry) => (
              <Card key={entry.id} className="border-cyan-500 bg-black/50">
                <CardContent className="p-6">
                  {editingEntry?.id === entry.id ? (
                    <div className="space-y-4">
                      <Textarea
                        value={editingEntry.content}
                        onChange={(e) => setEditingEntry({ ...editingEntry, content: e.target.value })}
                        className="bg-black border-cyan-500 text-cyan-400"
                        rows={4}
                        data-testid={`textarea-edit-${entry.id}`}
                      />
                      <div className="flex gap-2">
                        <Button
                          onClick={() => updateMutation.mutate(editingEntry)}
                          disabled={updateMutation.isPending}
                          className="bg-cyan-500 hover:bg-cyan-600 text-black"
                          data-testid={`button-update-${entry.id}`}
                        >
                          <Save className="w-4 h-4 mr-2" />
                          Update
                        </Button>
                        <Button
                          onClick={() => setEditingEntry(null)}
                          variant="outline"
                          className="border-cyan-500 text-cyan-400"
                          data-testid={`button-cancel-edit-${entry.id}`}
                        >
                          <X className="w-4 h-4 mr-2" />
                          Cancel
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex-1">
                          <p className="text-cyan-400 mb-2" data-testid={`text-content-${entry.id}`}>{entry.content}</p>
                          <div className="flex gap-2">
                            <Badge className="bg-cyan-500/20 text-cyan-400" data-testid={`badge-lang-${entry.id}`}>
                              {entry.language}
                            </Badge>
                            <Badge className="bg-cyan-500/20 text-cyan-400" data-testid={`badge-category-${entry.id}`}>
                              {entry.category}
                            </Badge>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            onClick={() => setEditingEntry(entry)}
                            variant="outline"
                            size="icon"
                            className="border-cyan-500 text-cyan-400"
                            data-testid={`button-edit-${entry.id}`}
                          >
                            <Edit2 className="w-4 h-4" />
                          </Button>
                          <Button
                            onClick={() => deleteMutation.mutate(entry.id)}
                            variant="outline"
                            size="icon"
                            className="border-red-500 text-red-400"
                            data-testid={`button-delete-${entry.id}`}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                      <p className="text-xs text-cyan-600">
                        Created: {new Date(entry.metadata.created_at).toLocaleString()}
                      </p>
                    </>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>

      <style>{`
        .neon-text {
          text-shadow: 0 0 10px #00FFFF, 0 0 20px #00FFFF, 0 0 30px #00FFFF;
        }
      `}</style>
    </div>
  );
}
