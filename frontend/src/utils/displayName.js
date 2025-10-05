export function userDisplayName(u) {
  if (!u) return "";
  return u.first_name?.trim() || u.username || "";
}
